# gpio_controller.py
import time
import platform

MOTOR_PINS = {
    1: 17,  # Physical pin 11
    2: 18,  # Physical pin 12
    3: 27,  # Physical pin 13
    4: 22,  # Physical pin 15
    5: 23,  # Physical pin 16
    6: 24,  # Physical pin 18
    7: 25,  # Physical pin 22
    8: 4,   # Physical pin 7
    9: 5,   # Physical pin 29
    10: 6,  # Physical pin 31
    11: 12, # Physical pin 32
    12: 13, # Physical pin 33
    13: 19, # Physical pin 35
    14: 16, # Physical pin 36
    15: 20, # Physical pin 38
    16: 21, # Physical pin 40
} # GROUND Physical pins (one ground connection should be fine): 6, 9, 14, 20, 25, 30, 34, 39

_initialized = False

def _is_raspberry_pi():
    # crude check for Raspberry Pi hardware
    return platform.machine().startswith("arm") or platform.uname().machine.startswith("arm")

if _is_raspberry_pi():
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    REAL_GPIO = True
else:
    # fallback mock for non-Pi systems
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

def init_pins():
    global _initialized
    if _initialized:
        return

    # Only try setup for real GPIO if we are on a Pi
    for pin in MOTOR_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

    _initialized = True

def trigger_motor(motor_id, duration=2):
    """Activate a motor (or mock it if not on Pi)"""
    init_pins()
    pin = MOTOR_PINS.get(motor_id)
    if not pin:
        return False

    print(f"[DEBUG] Activating Motor {motor_id} on pin {pin}")
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(pin, GPIO.LOW)
    print(f"[DEBUG] Motor {motor_id} deactivated")
    return True
