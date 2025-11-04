import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Booking, Payment
from .serializers import BookingSerializer, PaymentSerializer
from .tasks import send_booking_confirmation_email
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY', 'your_chapa_secret_key_here')
CHAPA_BASE_URL = 'https://api.chapa.co/v1/transaction'


@swagger_auto_schema(
    method='get',
    operation_description="Health check endpoint",
    responses={200: "Service is healthy"}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint for deployment monitoring."""
    return Response({
        'status': 'healthy',
        'message': 'ALX Travel App is running successfully',
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    Automatically triggers email notification upon booking creation.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @swagger_auto_schema(
        operation_description="Create a new booking and send confirmation email",
        request_body=BookingSerializer,
        responses={
            201: openapi.Response(
                description="Booking created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'booking': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new booking and trigger email notification asynchronously.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Get the created booking instance
        booking = serializer.instance

        # Prepare booking data for the email task
        booking_data = {
            'user_email': booking.user_email,
            'booking_reference': booking.booking_reference,
            'property_name': booking.property_name,
            'check_in_date': str(booking.check_in_date),
            'check_out_date': str(booking.check_out_date),
            'total_price': str(booking.total_price),
        }

        # Trigger the email task asynchronously using Celery
        send_booking_confirmation_email.delay(booking_data)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Booking created successfully. Confirmation email will be sent shortly.',
                'booking': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @swagger_auto_schema(
        method='post',
        operation_description="Initiate payment via Chapa API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['booking_reference', 'amount', 'email'],
            properties={
                'booking_reference': openapi.Schema(type=openapi.TYPE_STRING),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)
            }
        ),
        responses={
            200: openapi.Response(
                description="Payment initiated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'checkout_url': openapi.Schema(type=openapi.TYPE_STRING),
                        'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """Initiate payment via Chapa API."""
        booking_reference = request.data.get('booking_reference')
        amount = request.data.get('amount')
        email = request.data.get('email')

        if not all([booking_reference, amount, email]):
            return Response(
                {'error': 'booking_reference, amount, and email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payload = {
            'amount': amount,
            'currency': 'ETB',
            'email': email,
            'tx_ref': booking_reference,
            'callback_url': 'https://yourdomain.com/payment/verify/'
        }
        headers = {'Authorization': f'Bearer {CHAPA_SECRET_KEY}'}

        try:
            response = requests.post(f'{CHAPA_BASE_URL}/initialize', json=payload, headers=headers)
            resp_data = response.json()

            if resp_data.get('status') == 'success':
                transaction_id = resp_data['data']['tx_ref']
                payment = Payment.objects.create(
                    booking_reference=booking_reference,
                    amount=amount,
                    transaction_id=transaction_id,
                    status='Pending'
                )
                return Response({
                    'checkout_url': resp_data['data']['checkout_url'],
                    'payment_id': payment.id
                }, status=status.HTTP_200_OK)

            return Response(
                {'error': resp_data.get('message', 'Payment initiation failed')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Payment initiation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        method='post',
        operation_description="Verify payment status via Chapa API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['payment_id'],
            properties={
                'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Response(
                description="Payment verification result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request",
            404: "Payment not found",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify payment status via Chapa API."""
        payment_id = request.data.get('payment_id')

        if not payment_id:
            return Response(
                {'error': 'payment_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        headers = {'Authorization': f'Bearer {CHAPA_SECRET_KEY}'}

        try:
            response = requests.get(f'{CHAPA_BASE_URL}/verify/{payment.transaction_id}', headers=headers)
            resp_data = response.json()

            if resp_data.get('status') == 'success' and resp_data['data']['status'] == 'success':
                payment.status = 'Completed'
                payment.updated_at = timezone.now()
                payment.save()
                return Response({'status': 'Completed'}, status=status.HTTP_200_OK)
            else:
                payment.status = 'Failed'
                payment.updated_at = timezone.now()
                payment.save()
                return Response(
                    {'status': 'Failed', 'message': resp_data.get('message', 'Verification failed')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Payment verification failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
