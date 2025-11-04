# ALX Travel App Deployment Guide

## Overview
This guide covers deploying the ALX Travel App to production with Celery workers and public Swagger documentation.

## Deployment Options

### Option 1: Render (Recommended)

1. **Create a Render account** at https://render.com

2. **Create a new Web Service**:
   - Connect your GitHub repository
   - Choose "Python" as the environment
   - Build Command: `pip install -r requirements.txt && python deploy.py`
   - Start Command: `gunicorn alx_travel_app.wsgi:application`

3. **Add Environment Variables** in Render dashboard:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com
   CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   CHAPA_SECRET_KEY=your-chapa-key
   ```

4. **Create a Background Worker**:
   - Create another service for Celery worker
   - Start Command: `celery -A alx_travel_app worker --loglevel=info`

### Option 2: PythonAnywhere

1. **Create account** at https://www.pythonanywhere.com

2. **Upload your code** via Git or file upload

3. **Create a Web App**:
   - Choose Django
   - Set WSGI file path to your project

4. **Configure environment variables** in WSGI file

5. **Set up Celery** using scheduled tasks

## Environment Variables Required

```bash
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@host:port/db  # Optional
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CHAPA_SECRET_KEY=your-chapa-secret-key
```

## Testing Deployment

1. **Access Swagger Documentation**:
   - Visit: `https://your-domain.com/swagger/`
   - Should display interactive API documentation

2. **Test API Endpoints**:
   - Create a booking via `/api/bookings/`
   - Verify email notification is sent
   - Test payment initiation via `/api/payments/initiate/`

3. **Verify Celery Worker**:
   - Check logs for Celery task execution
   - Ensure email tasks are processed

## Troubleshooting

### Common Issues:

1. **Static files not loading**:
   - Ensure `STATIC_ROOT` is set correctly
   - Run `python manage.py collectstatic`

2. **Celery worker not starting**:
   - Check RabbitMQ/Redis connection
   - Verify `CELERY_BROKER_URL` environment variable

3. **Email not sending**:
   - Verify email credentials
   - Check email backend configuration

4. **Database connection issues**:
   - Ensure `DATABASE_URL` is correctly formatted
   - Run migrations: `python manage.py migrate`

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` configured properly
- [ ] Database credentials secured
- [ ] Email credentials secured
- [ ] HTTPS enabled (handled by hosting platform)

## API Documentation

Once deployed, your Swagger documentation will be available at:
- **Swagger UI**: `https://your-domain.com/swagger/`
- **ReDoc**: `https://your-domain.com/redoc/`

The documentation includes:
- All API endpoints
- Request/response schemas
- Interactive testing interface
- Authentication details