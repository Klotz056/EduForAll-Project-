# EduForAll - Educational Learning Platform

A comprehensive Django-based educational platform designed to facilitate online learning, course management, and student-mentor interaction. EduForAll provides a seamless experience for instructors to create and manage courses while enabling students to learn, track progress, and earn certifications.

## 🎯 Features

- **User Authentication**: Secure login and registration system for students and instructors
- **Course Management**: Instructors can create, update, and manage courses with detailed content
- **Student Enrollment**: Students can browse and enroll in available courses
- **Learning Dashboard**: Personalized dashboards for students to track their learning progress
- **Mentor Mentorship**: Dedicated mentor system for one-on-one student guidance
- **Real-time Messaging**: Built-in messaging system for student-mentor communication
- **Progress Tracking**: Monitor student progress and performance in courses
- **Certification**: Award certificates upon course completion
- **Learning Center**: Comprehensive resource library and educational materials
- **Newsletter System**: Stay updated with educational news and announcements
- **Responsive Design**: Mobile-friendly interface built with Bootstrap

## 🛠️ Tech Stack

- **Backend**: Django 6.0
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **JavaScript Libraries**: 
  - Owl Carousel (carousel functionality)
  - WOW.js (scroll animations)
  - Animate.css (animation effects)
- **Server**: Gunicorn (production)
- **Additional Tools**: WhiteNoise (static file serving)

## 📁 Project Structure

```
EduForAll-Project/
├── projectSchools/          # Main Django project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py             # Production WSGI configuration
│   └── asgi.py             # ASGI configuration
├── schoolApp/              # Main Django application
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── urls.py             # App URL routing
│   ├── admin.py            # Django admin configuration
│   ├── middleware.py       # Custom middleware
│   ├── migrations/         # Database migrations
│   └── templates/          # HTML templates
├── static/                 # Static files (CSS, JS, images)
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   ├── lib/               # Third-party libraries
│   └── img/               # Image assets
├── templates/             # Base templates
├── db.sqlite3            # SQLite database (development)
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd EduForAll-Project
```

### Step 2: Create and Activate Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

### Step 5: Apply Database Migrations
```bash
python manage.py migrate
```

### Step 6: Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### Step 7: Collect Static Files
```bash
python manage.py collectstatic
```

### Step 8: Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## 📖 Usage

### For Students
1. Navigate to the home page and click "Register"
2. Create your account with email and password
3. Browse available courses in the "Courses" section
4. Enroll in courses of interest
5. Access your learning dashboard to track progress
6. View course content and materials
7. Connect with mentors for guidance

### For Instructors/Mentors
1. Register as an instructor
2. Navigate to the mentor dashboard
3. Create new courses with detailed content
4. Manage enrolled students
5. Track student progress and performance
6. Send messages to students
7. Award certificates upon course completion

### Admin Panel
Access Django admin panel at `/admin`:
1. Create and manage courses
2. Manage user accounts and roles
3. View enrollment records
4. Monitor system activity

## 📊 Key Database Models

- **User**: Custom user model for authentication
- **Course**: Course information and metadata
- **Enrollment**: Student course enrollment records
- **Instructor**: Instructor profile and details
- **Mentor**: Mentor information and assignments
- **Student**: Student profile extensions
- **Newsletter**: Newsletter subscription and management
- **Message**: Student-mentor communication logs

## 🔧 Configuration

### Settings Location

Key settings:
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Add your domain in production
- `DATABASES`: Configure database connection
- `STATIC_FILES_STORAGE`: WhiteNoise for static file serving

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📝 Recent Updates

- Updated instructor profile images to SVG format
- Improved carousel section styling (75vh height)
- Enhanced responsive design for mobile devices
- Expanded messaging system functionality

## 📞 Support

For issues, bugs, or feature requests, please open an issue in the repository.

## 📄 License

This project is proprietary and intended for educational purposes only.

## 👥 Author

EduForAll Development Team

---

**Version**: 1.0.0  
**Last Updated**: March 2026
