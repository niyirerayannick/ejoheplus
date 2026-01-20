# EjoHePlus - Career Empowerment & Mentorship Platform

A production-ready Django web application for career empowerment, mentorship, and opportunities.

## Features

- **Role-Based Access Control**: Student, Mentor, Partner, and Administrator roles
- **Persistent Login**: Users stay logged in for 30 days across browser sessions
- **Mentorship Program**: Connect students with professional mentors
- **Career Library**: Explore career paths with detailed information
- **Opportunities**: Apply for scholarships, internships, jobs, and more
- **Training & E-Learning**: Enroll in courses, access materials, and earn certificates
- **Dashboards**: Role-specific dashboards with personalized features

## Technology Stack

- **Backend**: Django 5.0+ (LTS)
- **Frontend**: Django Templates + Tailwind CSS (CDN)
- **Database**: SQLite (development)
- **Authentication**: Django Session-based Authentication
- **API**: Django REST Framework (scaffolded)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository** (if applicable)
   ```bash
   cd ejoheplus
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (for admin access)
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Homepage: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Project Structure

```
ejoheplus/
├── accounts/          # User authentication & profiles
├── core/              # Core views & utilities
├── dashboard/         # Dashboard views for all roles
├── mentorship/        # Mentorship features
├── careers/           # Career library
├── opportunities/     # Opportunities & applications
├── training/          # Training & e-learning
├── templates/         # Django templates
│   ├── base.html
│   ├── home.html
│   ├── auth/
│   ├── dashboard/
│   ├── mentorship/
│   ├── careers/
│   ├── opportunities/
│   └── training/
├── ejoheplus/        # Project settings
└── manage.py
```

## User Roles

### Student
- View and apply for opportunities
- Connect with mentors
- Enroll in training courses
- Build and export CV
- Track application status

### Mentor
- Manage mentees
- Conduct mentorship sessions
- Upload resources
- Professional profile

### Partner
- Post opportunities
- View and manage applications
- Create events

### Administrator
- Full system management
- Approve mentors
- Manage all content
- View analytics and reports

## Authentication

The platform uses persistent session-based authentication:

- **Session Duration**: 30 days
- **Session Persistence**: Survives browser restarts
- **Login Required**: All dashboards are protected with `@login_required`

## Development

### Creating Test Data

1. Use Django admin panel to create users, careers, opportunities, and courses
2. Or create management commands for seeding test data

### Running Tests

```bash
python manage.py test
```

### Collecting Static Files (Production)

```bash
python manage.py collectstatic
```

## Production Deployment

Before deploying to production:

1. Set `DEBUG = False` in `settings.py`
2. Generate a new `SECRET_KEY`
3. Update `ALLOWED_HOSTS`
4. Configure a production database (PostgreSQL recommended)
5. Set up static file serving (WhiteNoise or CDN)
6. Configure media file storage
7. Set up HTTPS and update `SESSION_COOKIE_SECURE = True`

## License

Copyright © 2024 EjoHePlus

## Support

For support, please contact the development team.
