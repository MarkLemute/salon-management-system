# Salon Online Appointment Booking and Management System

> **Note:** This project is fully portable and can be deployed on any system with Python and MySQL. No system-specific configurations are hardcoded. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions on any platform.

## Project Description
The Salon Online Appointment Booking and Management System is a web-based information system developed to streamline and automate the process of scheduling salon services. The system enables customers to view available services and book appointments online, while providing administrators with tools to manage staff schedules, service offerings, and appointment records efficiently.

## Technology Stack
- **Backend:** Python (Django)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** MySQL
- **API Format:** JSON (REST)

## Features
- User registration and authentication
- View available services (haircut, braiding, manicure, etc.)
- View available time slots and prices
- Book/reschedule/cancel appointments
- Payment processing
- Admin dashboard for managing services and schedules
- Appointment status tracking
- Double booking prevention

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

### Setup Instructions

**Quick Start (Automated):**
```powershell
# Windows - Run automated setup script
.\setup.ps1
```

Then follow prompts and configure your .env file. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions.

**Manual Setup:**

1. Clone/download the repository:
```bash
# Clone from repository
git clone <repository-url>

# OR download and extract the ZIP file
# Then navigate to the project directory
cd path/to/salon_booking_system
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory (use `.env.example` as template):
```
DB_NAME=salon_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=your-secret-key-here
DEBUG=True
```

6. Create MySQL database:
```sql
CREATE DATABASE salon_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

7. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

**For Production Deployment:** See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide including Docker, Nginx, and cloud hosting options.

8. Create a superuser:
```bash
python manage.py createsuperuser
```

9. Run the development server:
```bash
python manage.py runserver
```

10. Access the application:
- Frontend: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## Project Structure
```
salon_booking_system/
├── backend/
│   ├── accounts/          # User authentication and management
│   ├── services/          # Service management
│   ├── staff/             # Staff management
│   ├── appointments/      # Appointment booking and management
│   ├── schedules/         # Schedule management
│   └── api/               # REST API endpoints
├── frontend/
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS, images
├── tests/                 # Unit and integration tests
├── requirements.txt       # Python dependencies
└── manage.py              # Django management script
```

## Main Modules

### 1. Accounts Module
- User registration, login, logout
- Role management (Admin, Staff, Customer)

### 2. Services Module
- Add/edit salon services
- Set price and duration

### 3. Staff Module
- Add staff members
- Assign services to staff

### 4. Schedules Module
- Set available time slots
- Define working hours

### 5. Appointments Module
- Book appointment
- Cancel/reschedule
- Status updates (Pending, Confirmed, Completed)

### 6. API Module
- REST endpoints for booking and data retrieval

## API Endpoints

### Book Appointment
```
POST /api/appointments/
Content-Type: application/json

{
  "user_id": 5,
  "service_id": 2,
  "staff_id": 1,
  "date": "2026-03-01",
  "time_slot": "10:00-11:00"
}
```

## Testing
Run tests with:
```bash
python manage.py test
```

## Database Schema
- **Users:** user_id, name, email, password, role
- **Services:** service_id, name, price, duration
- **Staff:** staff_id, name, specialization
- **Schedules:** schedule_id, staff_id, date, time_slot, availability_status
- **Appointments:** appointment_id, user_id, service_id, staff_id, schedule_id, status
- **Payment:** paymentID, paymentDate, appointment_id, amount

## Contributors
- Project developed as part of academic coursework

## License
This project is for educational purposes.
