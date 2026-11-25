
import tkinter as tk
from tkinter import ttk
import serial
import json
import csv
import os
import time
import threading
import urllib.request
import urllib.parse
from datetime import datetime


# SETTINGS


PORT = "/dev/ttyACM0"
BAUD = 9600

THINGSPEAK_WRITE_API_KEY = "XGOR29OD5GQM5GFN"

THINGSPEAK_INTERVAL = 16

LOG_FILE = "greenhouse_log.csv"

ser = None
pending_limits = None
last_upload = 0
last_message = ""

limits = {
    "lux": 100,
    "temp_low": 18,
    "temp_high": 32,
    "hum_low": 30,
    "hum_high": 80,
    "delta": 300
}


# ARDUINO CONNECTION


try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(2)
    ser.reset_input_buffer()
    print("Arduino connected:", PORT)

except Exception as e:
    print("Arduino connection failed:", e)


# CSV FILE


if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Time", "Temperature", "Humidity",
            "Light Lux", "Status"
        ])


# THINGSPEAK UPLOAD


def upload_to_thingspeak(temperature, humidity, lux):
    global last_upload

    if not THINGSPEAK_WRITE_API_KEY or \
       THINGSPEAK_WRITE_API_KEY == "XGOR29OD5GQM5GFN":
        return

    if time.monotonic() - last_upload < THINGSPEAK_INTERVAL:
        return

    last_upload = time.monotonic()

    data = {
        "api_key": THINGSPEAK_WRITE_API_KEY,
        "field1": temperature,
        "field2": humidity
    }

    if lux is not None:
        data["field3"] = lux

    encoded_data = urllib.parse.urlencode(data).encode()

    def send_data():
        try:
            request = urllib.request.Request(
                "https://api.thingspeak.com/update",
                data=encoded_data
            )

            with urllib.request.urlopen(request, timeout=10) as response:
                result = response.read().decode().strip()

            if result != "0":
                message = "ThingSpeak: Data uploaded"
                colour = "green"
            else:
                message = "ThingSpeak: Update rejected"
                colour = "red"

            root.after(
                0,
                lambda: thingspeak_status.config(
                    text=message, fg=colour
                )
            )

            print("ThingSpeak response:", result)

        except Exception as e:
            print("ThingSpeak error:", e)

            root.after(
                0,
                lambda: thingspeak_status.config(
                    text="ThingSpeak: Upload failed",
                    fg="red"
                )
            )

    threading.Thread(target=send_data, daemon=True).start()



# MAIN WINDOW


root = tk.Tk()
root.title("Smart Greenhouse Guardian")
root.geometry("900x760")
root.configure(bg="#edf2f7")

tk.Label(
    root,
    text="SMART GREENHOUSE GUARDIAN",
    font=("Arial", 23, "bold"),
    bg="#174c35",
    fg="white",
    pady=20
).pack(fill="x")

connection_label = tk.Label(
    root,
    text="Connected" if ser else "Arduino disconnected",
    font=("Arial", 11, "bold"),
    bg="#edf2f7",
    fg="green" if ser else "red"
)
connection_label.pack(pady=8)


# SENSOR CARDS


cards = tk.Frame(root, bg="#edf2f7")
cards.pack(pady=15)


def create_card(parent, title, unit):
    frame = tk.Frame(
        parent,
        bg="white",
        width=250,
        height=110,
        highlightbackground="#cbd5e0",
        highlightthickness=1
    )

    frame.pack_propagate(False)

    tk.Label(
        frame,
        text=title,
        font=("Arial", 12, "bold"),
        bg="white"
    ).pack(pady=(12, 4))

    value = tk.Label(
        frame,
        text="-- " + unit,
        font=("Arial", 22, "bold"),
        bg="white",
        fg="#174c35"
    )

    value.pack()

    return frame, value


temp_frame, temp_value = create_card(
    cards, "Temperature", "°C"
)

hum_frame, hum_value = create_card(
    cards, "Humidity", "%"
)

lux_frame, lux_value = create_card(
    cards, "Light Intensity", "lux"
)

temp_frame.grid(row=0, column=0, padx=8)
hum_frame.grid(row=0, column=1, padx=8)
lux_frame.grid(row=0, column=2, padx=8)


# STATUS LABELS


light_status = tk.Label(
    root,
    text="Light status: Waiting...",
    font=("Arial", 13, "bold"),
    bg="#edf2f7"
)
light_status.pack(pady=5)

alert_status = tk.Label(
    root,
    text="System status: Waiting...",
    font=("Arial", 13, "bold"),
    bg="#edf2f7"
)
alert_status.pack(pady=5)

thingspeak_status = tk.Label(
    root,
    text="ThingSpeak: Waiting for data...",
    font=("Arial", 11, "bold"),
    bg="#edf2f7"
)
thingspeak_status.pack(pady=5)


# THRESHOLD SETTINGS


settings = tk.LabelFrame(
    root,
    text="Configure Greenhouse Thresholds",
    font=("Arial", 12, "bold"),
    bg="#edf2f7",
    padx=10,
    pady=10
)

settings.pack(fill="x", padx=20, pady=12)

fields = [
    ("Minimum light (lux)", "lux", "100"),
    ("Minimum temperature", "temp_low", "18"),
    ("Maximum temperature", "temp_high", "32"),
    ("Minimum humidity (%)", "hum_low", "30"),
    ("Maximum humidity (%)", "hum_high", "80"),
    ("Drastic light change (lux)", "delta", "300")
]

entries = {}

for i, (label, key, default) in enumerate(fields):
    row = i // 3
    col = (i % 3) * 2

    tk.Label(
        settings,
        text=label,
        bg="#edf2f7"
    ).grid(row=row, column=col, padx=5, pady=8)

    entry = tk.Entry(settings, width=9)
    entry.insert(0, default)
    entry.grid(row=row, column=col + 1, padx=5)

    entries[key] = entry

settings_message = tk.Label(
    settings,
    text="",
    bg="#edf2f7"
)

settings_message.grid(row=2, column=0, columnspan=6)


# APPLY THRESHOLDS


def apply_limits():
    global pending_limits

    try:
        if not ser or not ser.is_open:
            raise ValueError("Arduino is not connected")

        if pending_limits is not None:
            raise ValueError("Previous update is pending")

        new_limits = {
            "lux": float(entries["lux"].get()),
            "temp_low": float(entries["temp_low"].get()),
            "temp_high": float(entries["temp_high"].get()),
            "hum_low": float(entries["hum_low"].get()),
            "hum_high": float(entries["hum_high"].get()),
            "delta": float(entries["delta"].get())
        }

        if new_limits["lux"] < 0:
            raise ValueError("Light threshold cannot be negative")

        if new_limits["temp_low"] >= new_limits["temp_high"]:
            raise ValueError("Minimum temperature must be lower")

        if new_limits["hum_low"] < 0 or \
           new_limits["hum_low"] >= new_limits["hum_high"] or \
           new_limits["hum_high"] > 100:
            raise ValueError("Invalid humidity limits")

        if new_limits["delta"] <= 0:
            raise ValueError("Light change must be positive")

        command = (
            f"LIMITS,"
            f"{new_limits['lux']},"
            f"{new_limits['temp_low']},"
            f"{new_limits['temp_high']},"
            f"{new_limits['hum_low']},"
            f"{new_limits['hum_high']},"
            f"{new_limits['delta']}\n"
        )

        pending_limits = new_limits.copy()

        ser.write(command.encode())
        ser.flush()

        settings_message.config(
            text="Waiting for Arduino confirmation...",
            fg="#c47a00"
        )

    except (ValueError, serial.SerialException) as e:
        pending_limits = None

        settings_message.config(
            text=str(e),
            fg="red"
        )


ttk.Button(
    settings,
    text="Apply Thresholds",
    command=apply_limits
).grid(row=3, column=0, columnspan=6, pady=8)


# ALERT HISTORY


history_frame = tk.LabelFrame(
    root,
    text="Recent Alert History",
    font=("Arial", 12, "bold"),
    bg="#edf2f7",
    padx=10,
    pady=8
)

history_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)

history = tk.Listbox(history_frame, height=7)
history.pack(fill="both", expand=True)


def add_history(message):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    history.insert(0, timestamp + " - " + message)

    if history.size() > 30:
        history.delete(30)



# PROCESS SENSOR READINGS


def process_reading(data):
    global last_message

    dht_available = data.get("dhtAvailable", True)
    light_available = data.get("lightAvailable", True)

    temperature = data.get("temperature")
    humidity = data.get("humidity")
    lux = data.get("lux")

    # Display DHT22 readings
    if dht_available and temperature is not None and humidity is not None:

        temperature = float(temperature)
        humidity = float(humidity)

        temp_value.config(text=f"{temperature:.1f} °C")
        hum_value.config(text=f"{humidity:.1f} %")

    else:
        temperature = None
        humidity = None

        temp_value.config(text="Unavailable")
        hum_value.config(text="Unavailable")

    # Display BH1750 reading
    if light_available and lux is not None:

        lux = float(lux)

        lux_value.config(text=f"{lux:.1f} lux")

        if data.get("lowLight", False):
            light_status.config(
                text="LOW LIGHT: Light is below threshold",
                fg="#c47a00"
            )
        else:
            light_status.config(
                text="Light level is within range",
                fg="green"
            )

    else:
        lux = None

        lux_value.config(text="Unavailable")

        light_status.config(
            text="BH1750 unavailable - light monitoring disabled",
            fg="red"
        )

    # Check environmental alerts
    problems = []

    if temperature is not None and humidity is not None:

        if temperature < limits["temp_low"]:
            problems.append("Temperature too low")

        if temperature > limits["temp_high"]:
            problems.append("Temperature too high")

        if humidity < limits["hum_low"]:
            problems.append("Humidity too low")

        if humidity > limits["hum_high"]:
            problems.append("Humidity too high")

    if light_available and data.get("drasticChange", False):
        problems.append("Drastic light change")

    if not dht_available:
        problems.append("DHT22 unavailable")

    if problems:

        message = "WARNING: " + ", ".join(problems)

        alert_status.config(text=message, fg="red")
        status = "ALERT"

    else:

        message = "All available conditions are normal"

        alert_status.config(text=message, fg="green")
        status = "NORMAL"

    if message != last_message:
        add_history(message)
        last_message = message

    # Save readings to CSV
    with open(LOG_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            temperature if temperature is not None else "",
            humidity if humidity is not None else "",
            lux if lux is not None else "",
            status
        ])

    # Upload to ThingSpeak when DHT22 is working
    if temperature is not None and humidity is not None:

        upload_to_thingspeak(
            temperature,
            humidity,
            lux
        )



# READ ARDUINO DATA


def read_serial():
    global pending_limits

    if ser and ser.is_open:

        try:

            while ser.in_waiting:

                line = ser.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not line:
                    continue

                print("Arduino:", line)

                if line == "ACK:LIMITS":

                    if pending_limits is not None:

                        limits.update(pending_limits)
                        pending_limits = None

                        settings_message.config(
                            text="Thresholds updated successfully!",
                            fg="green"
                        )

                elif line.startswith("ERROR:"):

                    pending_limits = None

                    settings_message.config(
                        text="Arduino rejected: " + line,
                        fg="red"
                    )

                else:

                    try:

                        data = json.loads(line)

                        if "temperature" in data or \
                           "dhtAvailable" in data:

                            process_reading(data)

                            connection_label.config(
                                text="Arduino connected",
                                fg="green"
                            )

                    except json.JSONDecodeError:
                        print("Unknown Arduino message:", line)

        except serial.SerialException as e:

            connection_label.config(
                text="Serial connection error",
                fg="red"
            )

            print("Serial error:", e)

    root.after(200, read_serial)



# CLOSE DASHBOARD


def close_app():

    if ser and ser.is_open:
        ser.close()

    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)

read_serial()
root.mainloop()
