# gpio_controller.py
import time

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    REAL_GPIO = True
except ImportError:
    # Fallback mock
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        HIGH = 1
        LOW = 0

        def setmode(self, mode): 
            print(f"[MOCK] GPIO mode set: {mode}")

        def setup(self, pin, mode): 
            print(f"[MOCK] Setup pin {pin} as {mode}")
        def output(self, pin, state): 
            print(f"[MOCK] Pin {pin} set to {'HIGH' if state else 'LOW'}")

    GPIO = MockGPIO()
    REAL_GPIO = False

# Define motor pins (just like before)
MOTOR_PINS = {
    1: 17,
    2: 18,
    3: 27,
    4: 22,
    5: 23,
    6: 24,
    7: 25,
    8: 4,
    9: 5,
    10: 6,
    11: 12,
    12: 13,
    13: 19,
    14: 16,
    15: 20,
    16: 21,
}

# Initialize pins
for pin in MOTOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def trigger_motor(motor_id, duration=2):
    """Activate a motor (or mock it)"""
    pin = MOTOR_PINS.get(motor_id)
    if not pin:
        return False
    
    print(f"[DEBUG] Activating Motor {motor_id} on pin {pin}")
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)
    print(f"[DEBUG] Motor {motor_id} deactivated")
    return True