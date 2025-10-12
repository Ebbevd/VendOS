# gpio_controller.py (Arduino serial with safe fallback)
import time

# Mapping motor IDs 1–16
MOTOR_IDS = list(range(1, 17))

# Serial connection (initialized later)
ser = None
REAL_ARDUINO = False

# Arduino serial port and baud rate
ARDUINO_PORT = '/dev/ttyACM0'  # change as needed
BAUD_RATE = 9600

# Arduino pinouts:
#const int RELAY_PINS[16] = {
  #22, 23, 24, 25, 26, 27, 28, 29,
  #30, 31, 32, 33, 34, 35, 36, 37
#};

# Try to initialize serial
try:
    import serial
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # give Arduino time to reset
    REAL_ARDUINO = True
    print(f"[INFO] Connected to Arduino on {ARDUINO_PORT}")
except Exception as e:
    print(f"[WARNING] Could not connect to Arduino: {e}")
    print("[INFO] Running in mock mode")
    ser = None

def trigger_motor(motor_id, duration=2):
    """
    Activate a motor via Arduino.
    motor_id: 1–16
    duration: seconds (converted to ms for Arduino)
    """
    if motor_id not in MOTOR_IDS:
        print(f"[ERROR] Invalid motor ID: {motor_id}")
        return False

    duration_ms = int(duration * 1000)
    cmd = f"{motor_id} {duration_ms}\n"

    if REAL_ARDUINO and ser is not None:
        try:
            ser.write(cmd.encode())
            print(f"[DEBUG] Sent command to Arduino: Motor {motor_id} for {duration_ms}ms")
        except Exception as e:
            print(f"[ERROR] Failed to send command to Arduino: {e}")
            print("[INFO] Running in mock mode")
    else:
        # mock mode if Arduino not connected
        print(f"[MOCK] Would activate Motor {motor_id} for {duration_ms}ms")

    return True

def close_serial():
    if REAL_ARDUINO and ser is not None:
        ser.close()
        print("[INFO] Serial port closed")
        
