from django.shortcuts import render
from django.http import JsonResponse
from VendOS.gpio_controller import trigger_motor

def test_motors_page(request):
    motors = range(1, 17)  # creates [1..16]
    return render(request, "tests/test_motors.html", {"motors": motors})

def test_motor(request, motor_id):
    if request.method == "POST":
        success = trigger_motor(motor_id)
        return JsonResponse({"success": success, "motor": motor_id})
    return JsonResponse({"success": False}, status=400)