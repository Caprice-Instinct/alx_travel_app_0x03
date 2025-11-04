# Quick Deploy - No Environment Variables Needed

## Deploy to Render (Zero Config)

1. **Fork this repository** to your GitHub

2. **Create Web Service on Render**:
   - Connect GitHub repo
   - Build Command: `pip install -r requirements.txt && python deploy.py`
   - Start Command: `gunicorn alx_travel_app.wsgi:application`

3. **Add Redis Add-on**:
   - In Render dashboard, add Redis add-on
   - This automatically sets `REDIS_URL` environment variable

4. **Create Background Worker**:
   - Create new Background Worker service
   - Start Command: `celery -A alx_travel_app worker --loglevel=info`

5. **Done!** Your app will be live at `https://your-app-name.onrender.com`

## What Works Out of the Box

- ✅ **API Documentation**: `/swagger/` and `/redoc/`
- ✅ **Health Check**: `/api/health/`
- ✅ **Booking API**: Creates bookings with email notifications
- ✅ **Payment API**: Chapa test integration
- ✅ **Background Tasks**: Celery with Redis

## Test Your Deployment

```bash
# Replace with your actual URL
curl https://your-app.onrender.com/api/health/
```

## Default Configuration

- **Email**: Console backend (logs to server)
- **Database**: SQLite (auto-created)
- **Payment**: Chapa test key included
- **Tasks**: Redis-based Celery
- **Debug**: False (production mode)

## Optional: Add Real Email

Only if you want real emails, add these environment variables:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

That's it! No other configuration needed.