from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from io import BytesIO
import os
import requests
import base64
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = "abc"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///econnect3.db'
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
    passing_year = db.Column(db.Integer, nullable=True)
    user_image = db.Column(db.LargeBinary, nullable=True)
    department = db.Column(db.String(20), nullable=True)
    course = db.Column(db.String(20), nullable=True)
    social1 = db.Column(db.String(150), nullable=True)
    social2 = db.Column(db.String(150), nullable=True)
    social3 = db.Column(db.String(150), nullable=True)
    social4 = db.Column(db.String(150), nullable=True)
    user = db.relationship('User', backref=db.backref('description', uselist=False))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user or admin is logged in
        if 'user_id' not in session and 'admin_id' not in session:
            flash("You need to log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
@login_required
def index():
    # Fetch all verified user cards for the initial page load
    cards = db.session.query(User, UserDesc).join(UserDesc, User.id == UserDesc.id).filter(User.is_verified == True).all()

    # Prepare card data with base64 encoded images for the template
    card_data = [{
        'id': user.id,
        'name': user.name,
        'course': desc.course,
        'department': desc.department,
        'passing_year': desc.passing_year,
        'short_desc': desc.short_desc,
        'user_image': base64.b64encode(desc.user_image).decode('utf-8') if desc.user_image else ''
    } for user, desc in cards]

    # Fetch unique dropdown values from user_desc
    departments = db.session.query(UserDesc.department).distinct().all()
    courses = db.session.query(UserDesc.course).distinct().all()
    passing_years = db.session.query(UserDesc.passing_year).distinct().all()
    
    return render_template('index.html', cards=card_data, departments=departments, courses=courses, passing_years=passing_years)

# Filtering cards on cards
@app.route('/filter_cards', methods=['POST'])
@login_required
def filter_cards():
    data = request.get_json()
    department = data.get('department')
    course = data.get('course')
    year_of_passing = data.get('year_of_passing')
    search_term = data.get('search_term')

    # Base query for verified users
    query = db.session.query(User, UserDesc).join(UserDesc, User.id == UserDesc.id).filter(User.is_verified == True)

    # Apply filters based on search criteria
    if department:
        query = query.filter(UserDesc.department == department)
    if course:
        query = query.filter(UserDesc.course == course)
    if year_of_passing:
        query = query.filter(UserDesc.passing_year == year_of_passing)
    if search_term:
        query = query.filter(
            (User.name.ilike(f"%{search_term}%")) | (User.enrollment_no.ilike(f"%{search_term}%"))
        )

    # Fetch filtered results
    results = query.all()

    # Convert results to JSON format for AJAX response
    response = [{
        'id': user.id,
        'name': user.name,
        'course': desc.course,
        'department': desc.department,
        'passing_year': desc.passing_year,
        'user_image': base64.b64encode(desc.user_image).decode('utf-8') if desc.user_image else ''
    } for user, desc in results]

    return jsonify(response)

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
@login_required
def verify_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_verified = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Delete users
@app.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.name} has been deleted.", "success")
    return redirect(url_for('admin_dashboard'))

# Admin Dashboard to see all unverified users
@app.route('/admindashboard')
@login_required
def admin_dashboard():
    unverified_users = User.query.filter_by(is_verified=False).all()
    return render_template('dashboard.html', users=unverified_users)

# Check ID
@app.route('/check_id/<int:user_id>')
@login_required
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
@login_required
def profile(user_id):
    if 'user_id' not in session:
        flash("You need to log in to view profiles.", "warning")
        return redirect(url_for('login'))
    user_data = db.session.query(User, UserDesc).join(UserDesc, User.id == UserDesc.id).filter(User.id == user_id).first()
    if user_data:
        user, user_desc = user_data
        user_image = base64.b64encode(user_desc.user_image).decode('utf-8') if user_desc.user_image else ''
        return render_template('profile.html', user=user, user_desc=user_desc, image = user_image)
    else:
        flash("User not found", "danger")
        return redirect(url_for('index'))

# Upload section
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("You need to log in to upload your details.", "warning")
        return redirect(url_for('login'))

    # Fetch the current user's data from the user table
    user = User.query.get(session['user_id'])
    user_desc = UserDesc.query.filter_by(id=user.id).first()

    if request.method == 'POST':
        # Collect data from the form submission
        short_desc = request.form['short_desc']
        detail_desc = request.form.get('detail_desc', '')
        passing_year = request.form['passing_year']
        department = request.form['department']
        course = request.form['course']
        user_image = request.files.get('user_image')  # Safely get the uploaded file

        # Check if user_image is provided
        if user_image:
            # Read the image file as a BLOB
            user_image_data = user_image.read()

        # Update or create a new entry in the user_desc table
        if user_desc:
            # Update existing user_desc
            user_desc.short_desc = short_desc
            user_desc.detail_desc = detail_desc
            user_desc.passing_year = passing_year
            user_desc.department = department
            user_desc.course = course
            if user_image:
                user_desc.user_image = user_image_data  # Store the image as a BLOB
        else:
            # Create new user_desc
            new_user_desc = UserDesc(
                id=user.id,
                short_desc=short_desc,
                detail_desc=detail_desc,
                passing_year=passing_year,
                user_image=user_image_data if user_image else None,
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
        return redirect(url_for('profile', user_id=user.id))  # Redirect to the user's profile page

    # Render the upload page with the user's data
    return render_template('upload.html', user=user, user_desc=user_desc)

# Logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
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