# Nextdoor Saloon - Online Appointment Booking and Management System

## Project Description
Nextdoor Saloon is a comprehensive web-based salon management system built with Django. The system streamlines the entire salon operation process, enabling customers to view available services and book appointments online while providing administrators and staff with powerful tools to manage schedules, services, and appointments efficiently.

## Technology Stack
- **Backend Framework:** Django 4.x
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Database:** MySQL with mysqlclient driver
- **API:** Django REST Framework
- **Additional Libraries:** 
  - django-cors-headers (CORS support)
  - python-dotenv (environment configuration)
  - Pillow (image processing)

## Key Features

### Customer Features
- 🔐 User registration and authentication
- 📋 Browse available salon services with detailed information
- 📅 View real-time staff availability and time slots
- 💇 Book appointments with preferred staff and services
- 🔄 Reschedule or cancel appointments
- 👤 Personal profile and appointment history
- 💰 View service prices and durations

### Staff Features
- 📊 Dedicated staff dashboard
- 📅 View and manage personal schedule
- 👥 Track assigned appointments
- ✅ Update appointment status
- 📝 Manage service assignments

### Admin Features
- 🎛️ Comprehensive admin panel
- 👨‍💼 Staff management (add, edit, assign services)
- 💼 Service management (create, update, pricing)
- 📆 Schedule management for all staff
- 📊 Appointment overview and management
- 🚫 Automatic double-booking prevention
- 📈 Real-time system monitoring

## Installation

### Prerequisites
- **Python:** 3.8 or higher
- **MySQL Server:** 5.7 or higher
- **pip:** Python package manager

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/MarkLemute/salon-management-system.git
cd salon-management-system
```

2. **Create and activate virtual environment:**
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in the project root directory:
```env
# Database Configuration
DB_NAME=salon_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. **Create MySQL database:**
```sql
CREATE DATABASE salon_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **Run database migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser (admin account):**
```bash
python manage.py createsuperuser
```

8. **Load sample data (optional):**
```bash
python manage.py populate_services
```

9. **Run the development server:**
```bash
python manage.py runserver
```

10. **Access the application:**
- **Main Site:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **API Endpoints:** http://localhost:8000/api/

## Project Structure
```
salon_booking_system/
├── backend/
│   ├── accounts/          # User authentication and role management
│   │   ├── models.py      # User model with role system
│   │   ├── views.py       # Login, registration, profile views
│   │   ├── decorators.py  # Role-based access decorators
│   │   └── validators.py  # Custom validators
│   ├── services/          # Service catalog management
│   │   ├── models.py      # Service model
│   │   ├── views.py       # Service CRUD operations
│   │   └── management/    # Custom commands (populate_services)
│   ├── staff/             # Staff and stylist management
│   │   ├── models.py      # Staff model with service assignments
│   │   └── views.py       # Staff CRUD and assignment
│   ├── appointments/      # Appointment booking system
│   │   ├── models.py      # Appointment model
│   │   ├── views.py       # Booking, cancellation, rescheduling
│   │   └── validators.py  # Booking validation logic
│   ├── schedules/         # Staff availability management
│   │   ├── models.py      # Schedule and time slot model
│   │   └── views.py       # Schedule CRUD operations
│   └── api/               # REST API endpoints
│       ├── serializers.py # DRF serializers
│       ├── views.py       # API viewsets
│       └── urls.py        # API routing
├── frontend/
│   ├── templates/         # Django HTML templates
│   │   ├── base.html      # Base template
│   │   ├── home.html      # Landing page
│   │   ├── booking.html   # Booking interface
│   │   ├── dashboard.html # Customer dashboard
│   │   ├── staff_dashboard.html  # Staff dashboard
│   │   └── admin_panel.html      # Admin interface
│   └── static/            
│       ├── css/           # Stylesheets
│       ├── js/            # JavaScript files
│       └── images/        # Static images
├── salon_booking_system/  # Django project configuration
│   ├── settings.py        # Project settings
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI configuration
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
└── README.md              # This file
```

## Application Modules

### 1. Accounts Module (`backend/accounts/`)
**Purpose:** User authentication and authorization

**Features:**
- User registration with email validation
- Secure login/logout system
- Three-tier role system (Admin, Staff, Customer)
- Profile management
- Role-based access control with custom decorators

**Key Models:**
- `User` (extends Django's AbstractUser)
  - Fields: username, email, password, role, phone_number, address

### 2. Services Module (`backend/services/`)
**Purpose:** Manage salon service catalog

**Features:**
- Create and manage service offerings
- Set pricing and duration
- Service categories (haircut, braiding, manicure, pedicure, etc.)
- Active/inactive service status
- Service descriptions and images

**Key Models:**
- `Service`
  - Fields: name, description, price, duration, category, is_active, image

### 3. Staff Module (`backend/staff/`)
**Purpose:** Staff member management

**Features:**
- Add and manage staff profiles
- Assign multiple services to staff members
- Track staff availability status
- Specialization management
- Staff photo management

**Key Models:**
- `Staff`
  - Fields: user (FK), specialization, is_available, services (M2M), photo, bio

### 4. Schedules Module (`backend/schedules/`)
**Purpose:** Manage staff working schedules

**Features:**
- Create recurring or one-time schedules
- Define available time slots
- Track slot availability (available/booked/unavailable)
- Prevent schedule conflicts
- Bulk schedule creation

**Key Models:**
- `Schedule`
  - Fields: staff (FK), date, time_slot, availability_status

### 5. Appointments Module (`backend/appointments/`)
**Purpose:** Core booking and appointment management

**Features:**
- Real-time appointment booking
- Double-booking prevention
- Appointment cancellation with policy enforcement
- Rescheduling functionality
- Status tracking (Pending, Confirmed, In Progress, Completed, Cancelled)
- Appointment history
- Email notifications (optional)

**Key Models:**
- `Appointment`
  - Fields: user (FK), service (FK), staff (FK), schedule (FK), status, notes, created_at, updated_at

### 6. API Module (`backend/api/`)
**Purpose:** RESTful API for external integrations

**Features:**
- JSON REST API endpoints
- Token-based authentication
- CORS support for frontend frameworks
- Comprehensive serialization
- API documentation

## API Endpoints

### Authentication
```http
POST /accounts/login/
POST /accounts/register/
POST /accounts/logout/
```

### Services
```http
GET  /api/services/              # List all active services
GET  /api/services/<id>/         # Service details
POST /api/services/              # Create service (admin only)
PUT  /api/services/<id>/         # Update service (admin only)
DELETE /api/services/<id>/       # Delete service (admin only)
```

### Staff
```http
GET  /api/staff/                 # List all available staff
GET  /api/staff/<id>/            # Staff details
GET  /api/staff/<id>/services/   # Services offered by staff
```

### Schedules
```http
GET  /api/schedules/             # Available time slots
GET  /api/schedules/?staff=<id>&date=<date>  # Filter by staff and date
```

### Appointments
```http
POST /api/appointments/          # Book appointment
GET  /api/appointments/          # List user's appointments
GET  /api/appointments/<id>/     # Appointment details
PUT  /api/appointments/<id>/     # Update/reschedule
DELETE /api/appointments/<id>/   # Cancel appointment
```

**Example Booking Request:**
```json
POST /api/appointments/
Content-Type: application/json

{
  "service_id": 2,
  "staff_id": 1,
  "schedule_id": 45,
  "notes": "First time customer"
}
```

**Example Response:**
```json
{
  "id": 123,
  "service": "Haircut & Styling",
  "staff": "Jane Smith",
  "date": "2026-03-01",
  "time_slot": "10:00-11:00",
  "status": "Pending",
  "created_at": "2026-02-12T14:30:00Z"
}
```

## Database Schema

### Core Tables

**Users**
- `id` (PK), `username`, `email`, `password` (hashed), `role`, `phone_number`, `address`, `date_joined`

**Services**
- `id` (PK), `name`, `description`, `price` (decimal), `duration` (minutes), `category`, `is_active`, `image`, `created_at`

**Staff**
- `id` (PK), `user_id` (FK), `specialization`, `is_available`, `photo`, `bio`, `joined_date`

**Staff_Services** (Many-to-Many)
- `staff_id` (FK), `service_id` (FK)

**Schedules**
- `id` (PK), `staff_id` (FK), `date`, `time_slot`, `availability_status`, `created_at`

**Appointments**
- `id` (PK), `user_id` (FK), `service_id` (FK), `staff_id` (FK), `schedule_id` (FK), `status`, `notes`, `created_at`, `updated_at`

## User Roles & Permissions

### Admin
- Full system access
- Manage all users, staff, services, and appointments
- View analytics and reports
- System configuration

### Staff
- View personal schedule
- Manage assigned appointments
- Update appointment status
- View customer information for their appointments

### Customer
- Browse services
- Book appointments
- View personal appointment history
- Update profile
- Cancel/reschedule own appointments

## Security Features

- 🔒 CSRF protection enabled
- 🔐 Password hashing with Django's PBKDF2
- 🛡️ SQL injection prevention (Django ORM)
- 🚫 XSS protection
- 🔑 Environment-based secret key management
- 👥 Role-based access control
- 🔓 Session security

## Development

### Running Development Server
```bash
python manage.py runserver
```

### Creating Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

### Populating Sample Services
```bash
python manage.py populate_services
```

### Checking for Issues
```bash
python manage.py check
```

## Production Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain(s)
- [ ] Use production database credentials
- [ ] Configure static files with `collectstatic`
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Enable email backend for notifications

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available for educational and commercial use.

## Support

For issues, questions, or suggestions:
- GitHub Issues: [Report an issue](https://github.com/MarkLemute/salon-management-system/issues)
- GitHub Repository: [salon-management-system](https://github.com/MarkLemute/salon-management-system)

## Author

**Mark Lemute**
- GitHub: [@MarkLemute](https://github.com/MarkLemute)

---

**Built with ❤️ using Django**


