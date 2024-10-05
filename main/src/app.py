from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import requests

app = Flask(__name__)

# Configure the SQLite3 database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///econnect.db'
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

    # Define relationship with User
    user = db.relationship('User', backref=db.backref('description', uselist=False))

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()


#Login page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if the user is admin
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            # Authenticate admin
            if check_password_hash(admin.password, password):
                session["admin_id"] = admin.id  # Store admin session
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Invalid admin credentials", "danger")
                return redirect(url_for("login"))

        # Check if the user is a regular user
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if the user is verified and password is correct
            if check_password_hash(user.password, password):
                if user.is_verified:
                    session["user_id"] = user.id  # Store user session
                    return redirect(url_for("index"))  # Redirect to home
                else:
                    flash("Your account is not verified yet. Please wait for admin approval.", "warning")
            else:
                flash("Invalid credentials", "danger")
        else:
            flash("User does not exist", "danger")

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
        # Collect form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        enrollment_no = request.form['enrollment_no']
        faculty_no = request.form['faculty_no']
        id_proof = request.files['id_proof']

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Save the id_proof file securely
        id_proof_filename = secure_filename(id_proof.filename)
        id_proof_path = os.path.join('uploads', id_proof_filename)
        id_proof.save(id_proof_path)

        # Create new user with is_verified set to False
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            enrollment_no=enrollment_no,
            faculty_no=faculty_no,
            id_proof=id_proof.read(),  # Store the file in BLOB format
            is_verified=False
        )

        # Add user to the database
        db.session.add(new_user)
        db.session.commit()

        # Flash a message and redirect to login page
        flash("Please wait till your verification", "info")
        return redirect(url_for('login'))

    return render_template('register.html')


# Route for admin to verify users
@app.route('/verify/<int:user_id>', methods=['GET', 'POST'])
def verify_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.is_verified = True
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('verify_user.html', user=user)

# Admin Dashboard to see all unverified users
@app.route('/admindashboard')
def admin_dashboard():
    unverified_users = User.query.filter_by(is_verified=False).all()
    return render_template('dashboard.html', users=unverified_users)


# Profile of Individual user
@app.route('/profile/<int:user_id>')
def profile(user_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("You need to log in to view profiles.", "warning")
        return redirect(url_for('login'))

    # Perform a join between the 'user' and 'user_desc' tables
    user_data = db.session.query(User, UserDesc).join(UserDesc, User.id == UserDesc.id).filter(User.id == user_id).first()

    if user_data:
        # user_data is a tuple (User object, UserDesc object)
        user, user_desc = user_data
        return render_template('profile.html', user=user, user_desc=user_desc)
    else:
        flash("User not found", "danger")
        return redirect(url_for('index'))  # Redirect to home if user not found

# Upload section
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("You need to log in to upload your details.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Collect form data
        short_desc = request.form['short_desc']
        detail_desc = request.form['detail_desc']
        passing_year = request.form['passing_year']
        department = request.form['department']
        course = request.form['course']
        user_image = request.files['user_image']

        # Save the user image file securely
        user_image_filename = secure_filename(user_image.filename)
        user_image_path = os.path.join('uploads', user_image_filename)
        user_image.save(user_image_path)

        # Create a new user description entry linked to the logged-in user
        new_user_desc = UserDesc(
            id=session['user_id'],  # Use the logged-in user's ID
            short_desc=short_desc,
            detail_desc=detail_desc,
            passing_year=passing_year,
            user_image=user_image.read(),  # Store the file as BLOB
            department=department,
            course=course,
            social1=request.form.get('social1', ''),
            social2=request.form.get('social2', ''),
            social3=request.form.get('social3', ''),
            social4=request.form.get('social4', '')
        )

        # Add the user description to the database
        db.session.add(new_user_desc)
        db.session.commit()

        flash("Your details have been uploaded successfully.", "success")
        return redirect(url_for('profile', user_id=session['user_id']))  # Redirect to the user's profile page

    return render_template('upload.html')

#About page - with a Random Quote from random-Quote-API
@app.route('/about')
def about():
    url = "https://api.freeapi.app/api/v1/public/quotes/quote/random"
    response = requests.get(url)

    data  = response.json() # Dictionary

    data_body = data["data"]
    quote = data_body["content"]
    author = data_body["author"]
    return render_template('about.html',  quote=quote, author=author)

if __name__ == "__main__":
    app.run(debug=True)
