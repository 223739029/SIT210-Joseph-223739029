import tkinter as tk
import RPi.GPIO as GPIO
import time
import threading
import board
import adafruit_dht
import requests
import pigpio

# --------------------- GPIO SETUP ---------------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pin Assignments
LED_BLUE        = 17
LED_TEMP_GREEN  = 27
LED_TEMP_RED    = 22
LED_HUM_GREEN   = 5
LED_HUM_RED     = 6
BUZZER          = 13
PIR             = 26
TRIG            = 23
ECHO            = 24
SERVO           = 12

# OUTPUT pins
GPIO.setup([LED_BLUE, LED_TEMP_GREEN, LED_TEMP_RED,
            LED_HUM_GREEN, LED_HUM_RED, BUZZER, TRIG], GPIO.OUT)

# INPUT pins
GPIO.setup(PIR, GPIO.IN)
GPIO.setup(ECHO, GPIO.IN)

# Servo Setup
pi = pigpio.pi()
pi.set_mode(SERVO, pigpio.OUTPUT)

# DHT11 setup
dhtDevice = adafruit_dht.DHT11(board.D4)

# --------------------- PARAMETERS ---------------------
ifttt_url = "https://maker.ifttt.com/trigger/AFK ALERT/with/key/dtPpX3MO_ZNxYWdr7FhDV"
last_motion_time = time.time()
mode_settings = {
    "Work":  {"water_interval": 20*60, "afk_limit": None},
    "Study": {"water_interval": 20*60, "afk_limit": 5*60},
    "Other": {"water_interval": 300,    "afk_limit": 15}
}
current_mode     = "Off"
water_timer      = None
monitoring       = True

# --------------------- FUNCTIONS ---------------------
def blink(pin, duration=4):
    GPIO.output(pin, True)
    time.sleep(duration)
    GPIO.output(pin, False)

def wave_servo():
    pi.set_servo_pulsewidth(SERVO, 1500); time.sleep(0.3)
    pi.set_servo_pulsewidth(SERVO, 2400); time.sleep(0.3)
    pi.set_servo_pulsewidth(SERVO, 1500); time.sleep(0.3)
    pi.set_servo_pulsewidth(SERVO, 0)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == 0:
        start = time.time()
    while GPIO.input(ECHO) == 1:
        end = time.time()
    return (end - start) * 17150

def read_dht():
    try:
        temperature = dhtDevice.temperature
        humidity    = dhtDevice.humidity
    except RuntimeError:
        return None, None
    return humidity, temperature

def send_ifttt_alert():
    try:
        requests.post(ifttt_url, json={"value1": f"Mode: {current_mode}"})
    except:
        print("IFTTT alert failed.")

def monitor_sensors():
    global last_motion_time
    while monitoring:
        motion_detected = GPIO.input(PIR)
        if motion_detected:
            last_motion_time = time.time()
            print("[DEBUG] Motion detected. Updating last_motion_time.")

        afk_limit = mode_settings.get(current_mode, {}).get("afk_limit")
        print(f"[DEBUG] Current mode: {current_mode}, AFK limit: {afk_limit}")

        print("[DEBUG] Getting distance...")
        try:
            dist = get_distance()
            print(f"[DEBUG] Distance: {dist:.2f} cm")
        except Exception as e:
            print(f"[ERROR] get_distance() failed: {e}")
            dist = None

        # Update presence status on GUI
        if motion_detected or (dist is not None and dist < 50):
            presence_var.set("Status: At Desk")
        else:
            presence_var.set("Status: Not at Desk")

        if afk_limit and last_motion_time is not None and dist is not None:
            time_since_motion = time.time() - last_motion_time
            print(f"[DEBUG] Time since last motion: {time_since_motion:.2f} sec")

            if dist > 600  and time_since_motion > afk_limit:
                print("[DEBUG] AFK condition met. Sending alert.")
                send_ifttt_alert()
                for _ in range(2):
                    blink(BUZZER)
                    wave_servo()
            else:
                print("[DEBUG] AFK condition not met.")
        else:
            print("[DEBUG] AFK check skipped — missing data.")

        time.sleep(1)

        hum, temp = read_dht()
        if hum is not None and temp is not None:
            # Temperature LEDs
            if 20 <= temp <= 25:
                GPIO.output(LED_TEMP_GREEN, GPIO.HIGH)
                GPIO.output(LED_TEMP_RED, GPIO.LOW)
                print("Temp OK → GREEN ON")
            else:
                GPIO.output(LED_TEMP_GREEN, GPIO.LOW)
                GPIO.output(LED_TEMP_RED, GPIO.HIGH)
                print("Temp BAD → RED ON")
                blink(BUZZER)
                wave_servo()

            # Humidity LEDs
            if 30 <= hum <= 60:
                GPIO.output(LED_HUM_GREEN, GPIO.HIGH)
                GPIO.output(LED_HUM_RED, GPIO.LOW)
                print("Humidity OK → GREEN ON")
            else:
                GPIO.output(LED_HUM_GREEN, GPIO.LOW)
                GPIO.output(LED_HUM_RED, GPIO.HIGH)
                print("Humidity BAD → RED ON")
                blink(BUZZER)
                wave_servo()
        else:
            print("[DEBUG] DHT read failed, skipping LED logic")

        time.sleep(2)

def water_reminder_loop():
    global water_timer
    interval = mode_settings.get(current_mode, {}).get("water_interval")
    if not interval:
        return

    for _ in range(3):
        GPIO.output(LED_BLUE, True)
        GPIO.output(BUZZER, True)
        wave_servo()
        time.sleep(0.2)
        GPIO.output(LED_BLUE, False)
        GPIO.output(BUZZER, False)
        time.sleep(0.2)

    water_timer = threading.Timer(interval, water_reminder_loop)
    water_timer.start()

def set_mode(mode):
    global current_mode, water_timer, last_motion_time
    current_mode = mode
    last_motion_time = time.time()
    if water_timer:
        water_timer.cancel()
    for led in [LED_BLUE, LED_TEMP_GREEN, LED_TEMP_RED, LED_HUM_GREEN, LED_HUM_RED, BUZZER]:
        GPIO.output(led, False)
    if mode != "Off" and mode_settings.get(mode, {}).get("water_interval"):
        water_reminder_loop()
    status_var.set(f"Mode: {mode}")

# --------------------- GUI ---------------------
root = tk.Tk()
root.title("Deskie")

status_var = tk.StringVar(value=f"Mode: {current_mode}")
temp_var   = tk.StringVar(value="Temp: --.- °C")
hum_var    = tk.StringVar(value="Humidity: --.- %")
presence_var = tk.StringVar(value="Status: Unknown")

tk.Label(root, textvariable=status_var, font=("Arial", 14)).pack(pady=5)
for m in ["Work", "Study", "Other", "Off"]:
    tk.Button(root, text=m, width=20, command=lambda mm=m: set_mode(mm)).pack(pady=2)

tk.Label(root, textvariable=temp_var, font=("Arial", 12)).pack(pady=5)
tk.Label(root, textvariable=hum_var,  font=("Arial", 12)).pack(pady=5)
tk.Label(root, textvariable=presence_var, font=("Arial", 12)).pack(pady=5)

def update_sensor_labels():
    hum, temp = read_dht()
    if hum is not None and temp is not None:
        temp_var.set(f"Temp: {temp:.1f} °C")
        hum_var.set(f"Humidity: {hum:.1f} %")
    else:
        temp_var.set("Temp: --.- °C")
        hum_var.set("Humidity: --.- %")
    root.after(2000, update_sensor_labels)

def on_close():
    global monitoring
    monitoring = False
    if water_timer:
        water_timer.cancel()
    pi.set_servo_pulsewidth(SERVO, 0)
    pi.stop()
    GPIO.cleanup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# --------------------- START ---------------------
threading.Thread(target=monitor_sensors, daemon=True).start()
update_sensor_labels()
root.mainloop()
