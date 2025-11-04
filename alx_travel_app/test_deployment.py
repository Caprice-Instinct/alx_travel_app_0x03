#!/usr/bin/env python
"""
Deployment test script for ALX Travel App
Tests all critical endpoints after deployment
"""
import requests
import json
import sys
from datetime import datetime, timedelta

def test_deployment(base_url):
    """Test deployed application endpoints"""
    print(f"Testing deployment at: {base_url}")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/api/health/")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test Swagger documentation
    try:
        response = requests.get(f"{base_url}/swagger/")
        if response.status_code == 200:
            print("✅ Swagger documentation accessible")
        else:
            print(f"❌ Swagger documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger documentation error: {e}")
    
    # Test booking creation
    try:
        booking_data = {
            "user_email": "test@example.com",
            "property_name": "Test Hotel",
            "check_in_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "total_price": "150.00"
        }
        
        response = requests.post(
            f"{base_url}/api/bookings/",
            json=booking_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            print("✅ Booking creation test passed")
            booking_ref = response.json()['booking']['booking_reference']
            
            # Test payment initiation
            payment_data = {
                "booking_reference": booking_ref,
                "amount": 150.00,
                "email": "test@example.com"
            }
            
            payment_response = requests.post(
                f"{base_url}/api/payments/initiate/",
                json=payment_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if payment_response.status_code == 200:
                print("✅ Payment initiation test passed")
            else:
                print(f"⚠️  Payment initiation test failed: {payment_response.status_code}")
                
        else:
            print(f"❌ Booking creation test failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    print("\n🎉 Deployment testing completed!")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <base_url>")
        print("Example: python test_deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    test_deployment(base_url)