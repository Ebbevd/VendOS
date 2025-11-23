from django.http import JsonResponse
from .models import Status
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from main.models import Product

@csrf_exempt
def update_status(request):
    print("[INFO] Updating status...")
    status = Status.objects.first()
    if status is None:
        status = Status.objects.create()
    
    if status.errored:
        return JsonResponse({"status": "errored"}, status=500)
        
    status.last_hardbeat = timezone.now().isoformat()
    status.save()
    return JsonResponse({"status": f"updated to {status.last_hardbeat}"})

def get_status(request):
    print("[INFO] Getting status...")
    status = Status.objects.first()
    if not status:
        status = Status.objects.create()
    
    if status.errored:
        return JsonResponse({"status": "errored"}, status=500)
        
    # Convert datetime to ISO string
    return JsonResponse({"lastBeat": status.last_hardbeat.isoformat()})

# Storage check API endpoints 
def get_storage_status(request):
    # When we have 5 products or less, we consider it 'low stock'
    print("[INFO] Getting storage status...")
    products = Product.objects.all()
    available_stock = sum([p.stock for p in products])
    
    if available_stock <= 5:
        return JsonResponse({"storage_status": "low_stock"}, status=200)
    else:
        return JsonResponse({"storage_status": "sufficient_stock"}, status=200)