from django.shortcuts import render
from django.http import JsonResponse
from VendOS.gpio_controller import trigger_motor
from payments.models import PaymentModel, RefundModel
from django.conf import settings

def test_motors_page(request):
    motors = range(1, 17)  # creates [1..16]
    return render(request, "tests/test_motors.html", {"motors": motors})

def test_landiong_page(request):  
    return render(request, "tests/test_landing.html")

def test_motor(request, motor_id):
    if request.method == "POST":
        success = trigger_motor(motor_id, duration=5)
        return JsonResponse({"success": success, "motor": motor_id})
    return JsonResponse({"success": False}, status=400)

def show_payment_info(request, test_mode):
    all_payments = PaymentModel.objects.filter(test=test_mode, paid=True)
    all_refunds = RefundModel.objects.filter(test=test_mode)

    # Limit displayed entries to 100 most recent
    payments = all_payments.order_by("-id")[:100]
    refunds = all_refunds.order_by("-id")[:100]

    total_payments = sum(p.amount for p in all_payments)
    total_refunds = sum(r.amount for r in all_refunds)
    net_total = total_payments - total_refunds

    context = {
        "payments": payments,
        "refunds": refunds,
        "total_payments": total_payments,
        "total_refunds": total_refunds,
        "net_total": net_total,
        "test_mode": test_mode,
    }
    return render(request, "tests/payment_info.html", context)