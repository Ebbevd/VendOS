# gpio_controller.py (Arduino serial with safe fallback)
import time

# Mapping motor IDs 1–16
MOTOR_IDS = list(range(1, 17))

# Serial connection (initialized later)
ser = None
REAL_ARDUINO = False

# Arduino baud rate
BAUD_RATE = 9600

# Try soft-import pyserial
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    print("[INFO] pyserial not installed. Running in mock mode.")
    SERIAL_AVAILABLE = False

def find_arduino_port():
    """
    Scan all connected serial ports and return the first likely Arduino port.
    Returns None if pyserial not available or no port found.
    """
    if not SERIAL_AVAILABLE:
        return None

    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'ttyACM' in port.device or 'ttyUSB' in port.device:
            return port.device
    return None

def connect_arduino():
    """
    Attempt to connect to the Arduino. Sets REAL_ARDUINO and ser globally.
    Falls back to mock mode if pyserial not available or connection fails.
    """
    global ser, REAL_ARDUINO
    port = find_arduino_port()
    if port is None:
        print("[WARNING] Arduino not found or pyserial unavailable. Running in mock mode.")
        REAL_ARDUINO = False
        ser = None
        return
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)  # allow Arduino to reset
        REAL_ARDUINO = True
        print(f"[INFO] Connected to Arduino on {port}")
    except Exception as e:
        print(f"[WARNING] Could not connect to Arduino on {port}: {e}")
        print("[INFO] Running in mock mode")
        ser = None
        REAL_ARDUINO = False

# Connect on import
connect_arduino()

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
        print(f"[MOCK] Would activate Motor {motor_id} for {duration_ms}ms")

    return True

def close_serial():
    if REAL_ARDUINO and ser is not None:
        ser.close()
        print("[INFO] Serial port closed")
