from django.shortcuts import render, redirect,  get_object_or_404
import stripe
import qrcode
import threading
import io
import base64
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from main.models import Product
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import PaymentModel, RefundModel
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
    
    payment, created = PaymentModel.objects.get_or_create(
            stripe_session_id = "", # Not known yet
            product_slot= product.slot_id,              
            amount = product.price)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': product.name},
                'unit_amount': int(product.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        metadata={
            "payment_id": payment.id,
            "product_slot": product.slot_id,
            "unit_price": product.price,
        },
        success_url="https://media.tenor.com/DpJdyKQKgYkAAAAj/cat-jump.gif",
        cancel_url="https://example.com/cancel",
    )
    
    payment.stripe_session_id = session.payment_intent
    payment.save()
    
    qr_code_base64 = generate_qr_code(session.url)  # your existing QR code function
    return render(request, "payments/checkout.html", {
        "product": product,
        "qr_code_base64": qr_code_base64,
        "stripe_session_id": session.payment_intent,
        "redirect_URL": request.build_absolute_uri(
        reverse('payment_success', kwargs={'session_id': session.payment_intent}) ),
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
    
    if not sig_header:
        print("Missing Stripe signature header")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        session = event["data"]["object"]
        print(f"Webhook received for payment_id: {session.get('id')}")
            
    except ValueError as e:
        print("Invalid payload:", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"Webhook verification failed: {e}")
        try:
            data = stripe.util.json.loads(payload)
            payment_intent = data.get("data", {}).get("object", {}).get("payment_intent")
            if payment_intent:
                print(f"Refund issued for payment_intent {payment_intent} due to webhook failure")
        except Exception as refund_error:
            print(f"Failed to issue refund: {refund_error}")
        return HttpResponse(status=400)

    print("Received event:", event["type"])  # log event type
    
    if event["type"] == "payment_intent.created":
        payment = PaymentModel.objects.filter(stripe_session_id=session["id"]).first()
        if payment:
            payment.most_recent_intent = "payment_intent.created"
            payment.save()
            print(f"Payment intent updated for {session['id']}")

    if event["type"] == "checkout.session.completed":
        payment_id = session["metadata"]["payment_id"]  
        payment = PaymentModel.objects.get(id=payment_id)
        if settings.DEBUG:
            test_mode = True
        else:
            test_mode = False
        payment.stripe_session_id = session["payment_intent"]
        payment.paid = True
        payment.test = test_mode
        payment.most_recent_intent = "checkout.session.completed"
        payment.save()
        print(f"Payment recorded for {session['id']}")
    return HttpResponse(status=200)

def check_payment(request, session_id):
    # Because we are working from a localhost we cannot use webhooks.
    payment = PaymentModel.objects.filter(stripe_session_id=session_id).first()

    # Dispense the product if paid
    if payment and payment.most_recent_intent:
        paid = payment.paid
        return JsonResponse({"paid": paid})
    else:
        # Object not found
        print(f"Payment object not found or no intent, redirecting to error page {payment}, {payment.most_recent_intent}")
        return JsonResponse({"paid": False, 'error': True})

def payment_success(request, session_id):
    if settings.DEBUG:  
        test_mode = True
    else:
        test_mode = False
    try:
        payment = get_object_or_404(PaymentModel, stripe_session_id=session_id)
        
    except PaymentModel.DoesNotExist:
         RefundModel.objects.create(
                stripe_charge=payment.stripe_session_id,
                amount=10,  # default amount if product is unknown
                reason=f"Something went wrong",
                test = test_mode
            )
         messages.error(request, "Something went wrong, we will refund you.")
    if payment.paid:
        try:
            product = get_object_or_404(Product, slot_id=payment.product_slot)
        except Product.DoesNotExist:
            RefundModel.objects.create(
                stripe_charge=payment.stripe_session_id,
                amount=10,  # default amount if product is unknown
                reason=f"Something went wrong",
                test = test_mode
            )
            messages.error(request, "Something went wrong, we will refund you.")
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
                
            RefundModel.objects.create(
                stripe_charge=payment.stripe_session_id,
                amount=10,  # default amount if product is unknown
                reason=f"Something went wrong",
                test = test_mode
            )
            return redirect('order_screen')
    else:
        print("Session not paid yet")
        return redirect('order_screen')
    

def dispense_api(request, product_id, dispense_time):
    product = Product.objects.get(id=product_id)
    product.stock -= 1
    product.save()

    def run_motor():
        try:
            gpio_controller.trigger_motor(product.motor_id, duration=dispense_time)
        except Exception as e:
            print(f"Motor error: {e}")

    threading.Thread(target=run_motor, daemon=True).start()
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

def error_page(request):  
    return render(request, "payments/error_page.html")