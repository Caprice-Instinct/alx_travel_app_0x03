# ALX Travel App - Production Deployment Guide

A comprehensive Django-based travel booking application with payment integration, email notifications, and public API documentation.

## 🚀 Features

- **Booking Management**: Create and manage travel bookings with automated confirmation
- **Payment Integration**: Secure payment processing via Chapa API
- **Email Notifications**: Automated booking confirmation emails via Celery
- **RESTful API**: Complete API for booking and payment operations
- **API Documentation**: Interactive Swagger/OpenAPI documentation
- **Production Ready**: Configured for cloud deployment with Celery workers

## 🛠 Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Task Queue**: Celery with RabbitMQ
- **Payment Gateway**: Chapa API
- **Email**: Django email backend with SMTP support
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Production Server**: Gunicorn with WhiteNoise

## 🌐 Access Points

- **API Base**: https://your-domain.com/api/
- **Swagger Documentation**: https://your-domain.com/swagger/
- **ReDoc Documentation**: https://your-domain.com/redoc/
- **Health Check**: https://your-domain.com/api/health/

## 🚀 Deployment Options

### Option 1: Render.com (Recommended)

1. **Fork this repository** to your GitHub account

2. **Create a new Web Service** on Render:
   - Connect your GitHub repository
   - Environment: Python
   - Build Command: `pip install -r requirements.txt && python deploy.py`
   - Start Command: `gunicorn alx_travel_app.wsgi:application`

3. **Add Environment Variables**:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CHAPA_SECRET_KEY=your-chapa-key
```

4. **Create Background Worker**:
   - Create another service for Celery
   - Start Command: `celery -A alx_travel_app worker --loglevel=info`

5. **Test Deployment**:
```bash
python test_deployment.py https://your-app.onrender.com
```

### Option 2: PythonAnywhere

1. **Create account** at https://www.pythonanywhere.com
2. **Upload your code** via Git or file upload
3. **Create a Web App**: Choose Django, set WSGI file path
4. **Configure environment variables** in WSGI file
5. **Set up Celery** using scheduled tasks

## 📚 API Documentation

### Interactive Documentation

Once deployed, access comprehensive API documentation at:
- **Swagger UI**: `https://your-domain.com/swagger/`
- **ReDoc**: `https://your-domain.com/redoc/`

### Key Endpoints

#### Bookings
- `GET /api/bookings/` - List all bookings
- `POST /api/bookings/` - Create booking (triggers email)
- `GET /api/bookings/{id}/` - Get booking details
- `PUT /api/bookings/{id}/` - Update booking
- `DELETE /api/bookings/{id}/` - Delete booking

#### Payments
- `POST /api/payments/initiate/` - Initiate Chapa payment
- `POST /api/payments/verify/` - Verify payment status
- `GET /api/payments/` - List payments

#### System
- `GET /api/health/` - Health check endpoint

### Example Usage

**Create Booking**:
```bash
curl -X POST https://your-app.com/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "user@example.com",
    "property_name": "Beach Resort",
    "check_in_date": "2024-12-01",
    "check_out_date": "2024-12-05",
    "total_price": "500.00"
  }'
```

**Initiate Payment**:
```bash
curl -X POST https://your-app.com/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking_reference": "BOOK-123456",
    "amount": 500.00,
    "email": "user@example.com"
  }'
```

## ⚙️ Configuration

### Required Environment Variables

```env
# Django Core
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database (Optional - uses SQLite by default)
DATABASE_URL=postgresql://user:pass@host:port/db

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Payment Gateway
CHAPA_SECRET_KEY=your-chapa-secret-key
```

## 🧪 Testing

### Test Deployment
```bash
python test_deployment.py https://your-deployed-app.com
```

### Manual Testing
1. Visit `/swagger/` for interactive API testing
2. Create a booking via API
3. Check email delivery
4. Test payment initiation
5. Verify Celery worker logs

## 🔧 Troubleshooting

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

## 🔒 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` configured properly
- [ ] Database credentials secured
- [ ] Email credentials secured
- [ ] HTTPS enabled (handled by hosting platform)

## 🆘 Support

For deployment issues or questions:
1. Check application logs
2. Test with `test_deployment.py` script
3. Verify environment variables
4. Review Celery worker status

---

**🎉 Ready to deploy!** Your ALX Travel App will be live with full API documentation and background task processing.