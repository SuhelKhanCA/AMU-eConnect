# <h1 align="center">**AMU-eConnect**</h1>

# Documentation

**AMU Econnect** is a comprehensive social connectivity platform built for educational institutions. The platform aims to foster collaboration, networking, and engagement among students, faculty, and potentially alumni. It provides a secure and user-friendly environment for users to create profiles, connect with peers, and explore professional and academic opportunities.

---

## Table of Contents

- [**AMU-eConnect**](#amu-econnect)
- [Documentation](#documentation)
  - [Table of Contents](#table-of-contents)
  - [Purpose](#purpose)
  - [Features](#features)
    - [User-Specific Features](#user-specific-features)
    - [Admin-Specific Features](#admin-specific-features)
    - [Platform-Wide Features](#platform-wide-features)
  - [Technology Stack](#technology-stack)
    - [Backend](#backend)
    - [Frontend](#frontend)
    - [Database](#database)
    - [Deployment](#deployment)
  - [Installation and Setup](#installation-and-setup)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Application Structure](#application-structure)
- [**Preview**](#preview)
  - [Index Page](#index-page)
  - [Login Page](#login-page)
  - [Upload Page](#upload-page)
  - [About Page](#about-page)
- [Future Enhancements](#future-enhancements)
- [Links](#links)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Connect with me](#connect-with-me)

---

## Purpose

The project addresses the need for a centralized platform within universities where students and faculty can:

- Build meaningful connections based on shared academic and professional interests.
- Easily search for peers and alumni by filtering criteria such as department, course, and year of graduation.
- Enhance their digital presence with integrated social media links.

This application also lays the groundwork for potential integration into alumni networks, strengthening relationships between current students and graduates.

---

## Features

### User-Specific Features

- **Secure Registration and Login**:
  - New users can register with a valid email address and password.
  - Passwords are hashed for secure storage.
- **Profile Management**:
  - Users can create and update their profiles with personal, academic, and professional details.
  - Profile customization includes short and detailed descriptions, images, and social media links.

### Admin-Specific Features

- **User Verification**:
  - Admins review and verify user profiles to ensure authenticity.
  - Verified users gain access to advanced features like profile display on the public feed.

### Platform-Wide Features

- **Search and Filter**:
  - Users can search for profiles using a combination of filters:
    - **Department**
    - **Course**
    - **Year of Passing**
    - **Name or Enrollment Number**
- **Responsive Design**:
  - The platform is fully responsive and mobile-friendly, ensuring accessibility on all devices.
- **Social Media Integration**:
  - Users can link their Facebook, Instagram, Twitter, and LinkedIn profiles to their AMU Econnect profile.

---

## Technology Stack

### Backend

- **Flask**: Python-based lightweight web framework for building the application.
- **Flask-SQLAlchemy**: ORM for managing the SQLite database.
- **WTForms**: Used for building and validating web forms.

### Frontend

- **HTML5, CSS3**: Core technologies for building web interfaces.
- **Bootstrap**: Framework for responsive and modern design.
- **JavaScript**: For client-side interactivity.

### Database

- **SQLite**: Lightweight, serverless database for fast and efficient data storage.

### Deployment

- **Render**: Hosting service for deploying the application with reliable performance.

---

## Installation and Setup

Follow these steps to set up the project locally:

### Prerequisites

- Python 3.8 or later
- Pip (Python package manager)
- Virtual environment tools (optional but recommended)

### Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/SuhelKhanCA/AMU-Econnect.git
   cd AMU-Econnect/eConnect
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Required Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:

   Create a `.env` file to store configuration variables like secret keys.

   ```properties
   SECRET_KEY=your_secret_key
   SQLALCHEMY_DATABASE_URI=sqlite:///econnect3.db
   ```

5. **Initialize the Database**:

   Open a Python shell and run the following commands:

   ```python
   from econnect import db
   db.create_all()
   ```

6. **Run the Application**:
   ```bash
   flask run
   or
   python econnect.py
   ```

---

## Application Structure

```
AMU-Econnect/
├── eConnect/
│   ├── static/           # Static assets (CSS, JS, images)
│   ├── templates/        # HTML templates for views
│   ├── __init__.py       # Flask app initialization
│   └── econnect.py       # Application entry point
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── .env                  # Environment variables
```

---

# **Preview**

## Index Page

![image](https://github.com/user-attachments/assets/9e93a6f8-7323-40d5-9bd4-4f1c473e83cb)

## Login Page

![image](https://github.com/user-attachments/assets/196b418c-e3bf-46ca-a71e-9376f89f041c)

## Upload Page

![image](https://github.com/user-attachments/assets/004ef70c-87d1-4203-8834-0b498e033b05)

## About Page

![image](https://github.com/user-attachments/assets/f9aa96dc-3d24-4109-9fc0-328ad3a8c198)

---

# Future Enhancements

The following features can further enhance the AMU Econnect platform:

1. **Integration with Alumni Network**:
   - Extend the application to allow alumni to create profiles and connect with students and faculty.
   - Enable mentorship programs and professional networking.
2. **Event Management**:
   - Include event creation and registration for webinars, seminars, and university gatherings.
3. **Real-Time Chat**:
   - Add a secure messaging system for users to communicate directly.
4. **Advanced Analytics**:
   - Provide data insights into user engagement, network growth, and profile views.

---

# Links

- GitHub Repository: [https://github.com/SuhelKhanCA/AMU-Econnect](https://github.com/SuhelKhanCA/AMU-Econnect)
- Deployed Application: [https://amu-econnect.onrender.com](https://amu-econnect.onrender.com)

---

# License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

# Acknowledgments

Special thanks to the contributors and mentors who guided this project, as well as the Flask and Bootstrap communities for their excellent documentation and support.

---

# Connect with me

- GitHub: [SuhelKhanCA](https://github.com/SuhelKhanCA)
- LinkedIn: [Suhel Khan](https://www.linkedin.com/in/suhelkhanska/)
- Twitter: [Suhel Khan](https://twitter.com/@suhelkhanalig)
- Email: suhelkhanca@gmail.com
