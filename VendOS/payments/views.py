from django.shortcuts import render, redirect,  get_object_or_404
import stripe
import qrcode
import io
import base64
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from main.models import Product
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import PaymentModel
from VendOS import gpio_controller

if settings.DEBUG:
    stripe.api_key = settings.STRIPE_SK_TEST
    if not settings.STRIPE_SK_TEST:
        raise ValueError("STRIPE_SK_TEST is not set in environment variables")
else:
    stripe.api_key = settings.STRIPE_SK_LIVE    
    if not settings.STRIPE_SK_LIVE:
        raise ValueError("STRIPE_SK_LIVE is not set in environment variables")

# Create your views here.
def checkout(request, product_slot):
    """Checkout page showing a payment QR code

    Returns:
        product: the product selected by the user
        qr_code_base64: a base64 encoded PNG of the stripe payment link
        stripe_session_id: the Stripe session ID to check payment status
        redirect_url: the URL to redirect to after payment
    """
    product = get_object_or_404(Product, slot_id=product_slot)

    # Create a Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100),  # Stripe uses cents
            },
            'quantity': 1,
        }],
        mode='payment',
        metadata={
        'product_slot': product.slot_id  
        },
        success_url="https://media.tenor.com/DpJdyKQKgYkAAAAj/cat-jump.gif",  # Stripe will show its default page if you use a URL
        cancel_url="https://example.com/cancel",
    )

    qr_code_base64 = generate_qr_code(session.url)  # your existing QR code function
    time_out = 600 # seconds before redirecting to splash screen
    return render(request, "payments/checkout.html", {
        "time_out": time_out,
        "product": product,
        "qr_code_base64": qr_code_base64,
        "stripe_session_id": session.id,
        "redirect_URL": request.build_absolute_uri(
        reverse('payment_success', kwargs={'session_id': session.id}) ),
    })
    
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    if settings.DEBUG:
        endpoint_secret = settings.NGROK_TEST 
    else:
        endpoint_secret = settings.NGROK_SEC

    print(f"Calling webhook endpoint {endpoint_secret} with sig header {sig_header}")

    if not sig_header:
        print("Missing Stripe signature header")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        print("Invalid payload:", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature:", e)
        return HttpResponse(status=400)

    print("Received event:", event["type"])  # log event type

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        product_slot = session["metadata"].get("product_slot")
        PaymentModel.objects.create(
            product_slot=product_slot,
            stripe_session_id=session["id"],
            paid=True
        )
        print(f"Payment recorded for slot {product_slot} and session {session['id']}")

    return HttpResponse(status=200)

def check_payment(request, session_id):
    # Because we are working from a localhost we cannot use webhooks.
    payment = PaymentModel.objects.filter(stripe_session_id=session_id).first()

    # Dispense the product if paid
    if payment:
        paid = payment.paid
        return JsonResponse({"paid": paid})
    else:
        # Object not found
        return JsonResponse({"paid": False})

def payment_success(request, session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    paid = session.payment_status == "paid"
    
    if paid:
        product = get_object_or_404(Product, slot_id=session.metadata['product_slot'])
        if product.stock > 0:
            dispense_time = 5
            context = {
                "product": product,
                "dispense_time": dispense_time,
            }
            return render(request, "payments/product_dispense.html", context)
            # Dispensing will happen within the java script code
        else:
            messages.error(request, "Something went wrong, we will refund you.")
            # Refund the payment
            return redirect('order_screen')
    else:
        print("Session not paid yet")
        return redirect('order_screen')
    

def dispense_api(request, product_id, dispense_time):
    product = Product.objects.get(id=product_id)
    gpio_controller.trigger_motor(product.motor_id, duration=dispense_time)
    return JsonResponse({"status": "dispensing"})


def generate_qr_code(data):
    """
    Generates a base64-encoded PNG QR code from a string (URL or text).
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
    return qr_code_base64