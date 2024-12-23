from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from io import BytesIO
import os
import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = "abc"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///econnect2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Admin table model
class Admin(db.Model):
    __tablename__ = 'econnect_admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# User table model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    enrollment_no = db.Column(db.String(10), nullable=True)
    faculty_no = db.Column(db.String(10), nullable=True)
    id_proof = db.Column(db.LargeBinary, nullable=False)
    id_proof_mime = db.Column(db.String(50), nullable=True)  # New MIME type column
    is_verified = db.Column(db.Boolean, default=False)

# User Description table model
class UserDesc(db.Model):
    __tablename__ = 'user_desc'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    short_desc = db.Column(db.String(250), nullable=True)
    detail_desc = db.Column(db.Text, nullable=True)
    passing_year = db.Column(db.Numeric(4), nullable=True)
    user_image = db.Column(db.LargeBinary, nullable=False)
    department = db.Column(db.String(20), nullable=True)
    course = db.Column(db.String(20), nullable=True)
    social1 = db.Column(db.String(150), nullable=True)
    social2 = db.Column(db.String(150), nullable=True)
    social3 = db.Column(db.String(150), nullable=True)
    social4 = db.Column(db.String(150), nullable=True)
    user = db.relationship('User', backref=db.backref('description', uselist=False))

# Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if the user is admin
        admin = Admin.query.filter_by(email=email).first()
        if admin and admin.password == password:
            session["admin_id"] = admin.id
            return redirect(url_for("admin_dashboard"))

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if user.is_verified:
                session["user_id"] = user.id
                return redirect(url_for("index"))
            else:
                flash("Your account is not verified yet. Please wait for admin approval.", "warning")
        else:
            flash("Invalid credentials", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")

# Home page
@app.route('/home')
def index():
    verified_users = db.session.query(User, UserDesc).join(UserDesc, User.id == UserDesc.id).filter(User.is_verified == True).all()
    return render_template('index.html', users=verified_users)

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        enrollment_no = request.form['enrollment_no']
        faculty_no = request.form['faculty_no']
        id_proof = request.files['id_proof']
        id_proof_mime = id_proof.mimetype
        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            enrollment_no=enrollment_no,
            faculty_no=faculty_no,
            id_proof=id_proof.read(),
            id_proof_mime=id_proof_mime,
            is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Please wait till your verification", "info")
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for admin to verify users
@app.route('/verify/<int:user_id>', methods=['POST'])
def verify_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_verified = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Delete users
@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.name} has been deleted.", "success")
    return redirect(url_for('admin_dashboard'))

# Admin Dashboard to see all unverified users
@app.route('/admindashboard')
def admin_dashboard():
    if not session.get('admin_id'):
        flash("You need admin access to view this page.", "danger")
        return redirect(url_for('login'))
    
    unverified_users = User.query.filter_by(is_verified=False).all()
    return render_template('dashboard.html', users=unverified_users)


# Check ID
@app.route('/check_id/<int:user_id>')
def check_id(user_id):
    user = User.query.get_or_404(user_id)
    if user.id_proof and user.id_proof_mime == 'application/pdf':
        return send_file(
            BytesIO(user.id_proof), 
            as_attachment=False,
            download_name=f'{user.name}_ID_proof.pdf',
            mimetype='application/pdf'
        )
    else:
        flash("ID proof is not available or is not a PDF file.", "warning")
        return redirect(url_for('admin_dashboard'))

# Profile of Individual user
@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        flash("You need to log in to view profiles.", "warning")
        return redirect(url_for('login'))
    user_data = db.session.query(User, UserDesc).join(UserDesc, User.id == UserDesc.id).filter(User.id == user_id).first()
    if user_data:
        user, user_desc = user_data
        return render_template('profile.html', user=user, user_desc=user_desc)
    else:
        flash("User not found", "danger")
        return redirect(url_for('index'))

# Upload section
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash("You need to log in to upload your details.", "warning")
        return redirect(url_for('login'))
    if request.method == 'POST':
        short_desc = request.form['short_desc']
        detail_desc = request.form['detail_desc']
        passing_year = request.form['passing_year']
        department = request.form['department']
        course = request.form['course']
        user_image = request.files['user_image']
        
        new_user_desc = UserDesc(
            id=session['user_id'],
            short_desc=short_desc,
            detail_desc=detail_desc,
            passing_year=passing_year,
            user_image=user_image.read(),
            department=department,
            course=course,
            social1=request.form.get('social1', ''),
            social2=request.form.get('social2', ''),
            social3=request.form.get('social3', ''),
            social4=request.form.get('social4', '')
        )
        db.session.add(new_user_desc)
        db.session.commit()
        flash("Your details have been uploaded successfully.", "success")
        return redirect(url_for('profile', user_id=session['user_id']))
    return render_template('upload.html')

# Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

# About page - with a Random Quote from random-Quote-API
@app.route('/about')
def about():
    url = "https://api.freeapi.app/api/v1/public/quotes/quote/random"
    response = requests.get(url)
    data = response.json()
    data_body = data["data"]
    quote = data_body["content"]
    author = data_body["author"]
    return render_template('about.html',  quote=quote, author=author)

if __name__ == "__main__":
    app.run(debug=True)