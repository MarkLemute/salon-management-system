# Salon Management System - Deployment Guide

This guide will help you deploy the Salon Management System on any machine or server.

## 📋 Prerequisites

Before deploying, ensure you have:
- Python 3.8 or higher installed
- MySQL Server 5.7+ or 8.0+ installed
- Git (if cloning from repository)
- Basic knowledge of command line/terminal

## 🚀 Quick Setup (Any System)

### Step 1: Get the Project

**Option A: Clone from Git**
```bash
git clone <repository-url>
cd salon_booking_system
```

**Option B: Download & Extract**
- Download the project ZIP file
- Extract to your desired location
- Open terminal/command prompt in the extracted folder

### Step 2: Run Automated Setup Script

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
# Make the script executable (if you create a bash version)
chmod +x setup.sh
./setup.sh
```

### Step 3: Configure Your Database

1. Edit the `.env` file created by the setup script:
   ```bash
   # Windows
   notepad .env
   
   # Linux/Mac
   nano .env
   ```

2. Update these values with YOUR credentials:
   ```env
   DB_NAME=salon_db
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306
   SECRET_KEY=generate-a-long-random-string-here
   DEBUG=True
   ```

3. Generate a secure SECRET_KEY (Python):
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Step 4: Create MySQL Database

```sql
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE salon_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# (Optional) Create dedicated user
CREATE USER 'salon_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON salon_db.* TO 'salon_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 5: Initialize Database

```bash
# Activate virtual environment first
# Windows:
.\venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin account
python manage.py createsuperuser
```

### Step 6: Start the Server

```bash
python manage.py runserver
```

Access at: http://localhost:8000

---

## 🔧 Manual Setup (If Script Fails)

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy example file
cp .env.example .env  # Linux/Mac
copy .env.example .env  # Windows

# Edit .env with your settings
```

### 5. Follow Steps 4-6 from Quick Setup

---

## 🌐 Production Deployment

### Security Checklist
- [ ] Set `DEBUG=False` in .env
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` in .env
- [ ] Use strong database passwords
- [ ] Setup HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Setup regular database backups

### Recommended Production Setup

**Web Server:** Nginx or Apache
**WSGI Server:** Gunicorn or uWSGI
**Database:** MySQL 8.0+ or PostgreSQL
**Process Manager:** Supervisor or systemd

### Example: Deploy with Gunicorn & Nginx

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn service file** (`/etc/systemd/system/salon.service`):
   ```ini
   [Unit]
   Description=Salon Management System
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/salon_booking_system
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:salon.sock salon_booking_system.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

3. **Configure Nginx** (`/etc/nginx/sites-available/salon`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location /static/ {
           alias /path/to/salon_booking_system/staticfiles/;
       }

       location /media/ {
           alias /path/to/salon_booking_system/media/;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/path/to/salon_booking_system/salon.sock;
       }
   }
   ```

4. **Collect Static Files:**
   ```bash
   python manage.py collectstatic
   ```

5. **Start Services:**
   ```bash
   sudo systemctl start salon
   sudo systemctl enable salon
   sudo systemctl restart nginx
   ```

---

## 🐳 Docker Deployment (Alternative)

### Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "salon_booking_system.wsgi:application"]
```

### Create docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: salon_db
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql

  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DB_HOST=db
      - DB_NAME=salon_db
      - DB_USER=root
      - DB_PASSWORD=rootpassword

volumes:
  mysql_data:
```

### Run with Docker
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## 🧪 Testing Deployment

1. **Check Django is running:**
   ```bash
   curl http://localhost:8000
   ```

2. **Access admin panel:**
   ```
   http://localhost:8000/admin
   ```

3. **Test API endpoints:**
   ```bash
   curl http://localhost:8000/api/services/
   ```

---

## 🔍 Troubleshooting

### Issue: Port 8000 already in use
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Kill the process or use different port
python manage.py runserver 8080
```

### Issue: MySQL connection failed
- Verify MySQL service is running
- Check credentials in .env
- Ensure database exists
- Test connection: `mysql -u username -p`

### Issue: Module not found errors
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Static files not loading
```bash
# Run collectstatic
python manage.py collectstatic

# Check STATIC_ROOT in settings.py
```

---

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_NAME` | Database name | `salon_db` |
| `DB_USER` | Database username | `root` or `salon_user` |
| `DB_PASSWORD` | Database password | `your_password` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `3306` |
| `SECRET_KEY` | Django secret key | `long-random-string` |
| `DEBUG` | Debug mode | `True` (dev), `False` (prod) |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,yourdomain.com` |

---

## 📧 Support

For issues or questions:
1. Check SETUP_GUIDE.md for detailed instructions
2. Check README.md for project overview
3. Review error logs in the terminal
4. Check Django documentation: https://docs.djangoproject.com

---

## ✅ Post-Deployment Checklist

- [ ] Project files extracted/cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] MySQL database created
- [ ] Migrations run successfully
- [ ] Superuser created
- [ ] Server starts without errors
- [ ] Admin panel accessible
- [ ] Frontend pages load correctly
- [ ] API endpoints respond

---

**Note:** This project is designed to be portable and work on any system with Python and MySQL installed. No system-specific configurations are hardcoded.
