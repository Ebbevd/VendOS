from django.shortcuts import render, redirect,  get_object_or_404
import stripe
import qrcode
import io
import base64
from django.http import JsonResponse
from django.urls import reverse
from main.models import Product
from django.conf import settings
from django.contrib import messages

if settings.DEBUG:
    stripe.api_key = settings.STRIPE_SK_TEST
    endpoint_secret = settings.STRIPE_WH_SECRET
    if not endpoint_secret:
        raise ValueError("STRIPE_WH_SECRET is not set in environment variables")
    elif not settings.STRIPE_SK_TEST:
        raise ValueError("STRIPE_SK_TEST is not set in environment variables")
else:
    stripe.api_key = settings.STRIPE_SK_LIVE    
    endpoint_secret = settings.STRIPE_WH_SECRET
    if not endpoint_secret:
        raise ValueError("STRIPE_WH_SECRET is not set in environment variables")
    elif not settings.STRIPE_SK_LIVE:
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
    return render(request, "payments/checkout.html", {
        "product": product,
        "qr_code_base64": qr_code_base64,
        "stripe_session_id": session.id,
        "redirect_URL": request.build_absolute_uri(
        reverse('payment_success', kwargs={'session_id': session.id}) ),
    })

def check_payment(request, session_id):
    # Because we are working from a localhost we cannot use webhooks.
    session = stripe.checkout.Session.retrieve(session_id)
    paid = session.payment_status == "paid"

    # Dispense the product if paid
    if paid:
        return JsonResponse({"paid": True})
    else:
        return JsonResponse({"paid": False})

def payment_success(request, session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    paid = session.payment_status == "paid"
    
    if paid:
        product = get_object_or_404(Product, slot_id=session.metadata['product_slot'])
        if product.stock > 0:
            return render(request, "payments/product_dispense.html", {"product": product})
            # Dispensing will happen within the java script code
        else:
            messages.error(request, "Something went wrong, we will refund you.")
            # Refund the payment
            return redirect('order_screen')
    else:
        print("Session not paid yet")
        return redirect('order_screen')
    
def dispense_product(product):
    pass # will do later


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