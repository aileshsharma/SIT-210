import tkinter as tk
from tkinter import ttk
import serial
import json
import csv
import os
import time
from datetime import datetime

# ==========================================
# SERIAL CONFIGURATION
# ==========================================

PORT = "/dev/ttyACM0"
BAUD = 9600

ser = None
last_message = ""
pending_limits = None

log_file = "greenhouse_log.csv"

# ==========================================
# DEFAULT THRESHOLDS
# ==========================================

limits = {
    "lux": 100.0,
    "temp_low": 18.0,
    "temp_high": 32.0,
    "hum_low": 30.0,
    "hum_high": 80.0,
    "delta": 300.0
}

# ==========================================
# CONNECT TO ARDUINO
# ==========================================

try:
    ser = serial.Serial(
        PORT,
        BAUD,
        timeout=0.1,
        write_timeout=2
    )

    # Allow Arduino to restart after USB connection
    time.sleep(2)

    ser.reset_input_buffer()

    print("Arduino connected:", PORT)

except serial.SerialException as e:
    print("Arduino connection failed:", e)

# ==========================================
# CSV FILE
# ==========================================

if not os.path.exists(log_file):

    with open(log_file, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "Time",
            "Temperature",
            "Humidity",
            "Light Lux",
            "Status"
        ])

# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()

root.title("Smart Greenhouse Guardian")
root.geometry("900x720")
root.configure(bg="#edf2f7")

# ==========================================
# HEADER
# ==========================================

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

# ==========================================
# SENSOR DISPLAY CARDS
# ==========================================

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

# ==========================================
# STATUS MESSAGES
# ==========================================

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

# ==========================================
# THRESHOLD SETTINGS
# ==========================================

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

settings_message.grid(
    row=2,
    column=0,
    columnspan=6
)

# ==========================================
# APPLY NEW THRESHOLDS
# ==========================================

def apply_limits():

    global pending_limits

    try:

        if not ser or not ser.is_open:
            raise ValueError("Arduino is not connected")

        if pending_limits is not None:
            raise ValueError("Previous threshold update is pending")

        new_limits = {
            "lux": float(entries["lux"].get()),
            "temp_low": float(entries["temp_low"].get()),
            "temp_high": float(entries["temp_high"].get()),
            "hum_low": float(entries["hum_low"].get()),
            "hum_high": float(entries["hum_high"].get()),
            "delta": float(entries["delta"].get())
        }

        # Validate thresholds

        if new_limits["lux"] < 0:
            raise ValueError("Light threshold cannot be negative")

        if new_limits["temp_low"] >= new_limits["temp_high"]:
            raise ValueError(
                "Minimum temperature must be lower"
            )

        if new_limits["hum_low"] >= new_limits["hum_high"]:
            raise ValueError(
                "Minimum humidity must be lower"
            )

        if not (
            0 <= new_limits["hum_low"] <= 100 and
            0 <= new_limits["hum_high"] <= 100
        ):
            raise ValueError(
                "Humidity limits must be 0–100"
            )

        if new_limits["delta"] <= 0:
            raise ValueError(
                "Light change must be positive"
            )

        # Prepare serial command

        command = (
            f"LIMITS,"
            f"{new_limits['lux']},"
            f"{new_limits['temp_low']},"
            f"{new_limits['temp_high']},"
            f"{new_limits['hum_low']},"
            f"{new_limits['hum_high']},"
            f"{new_limits['delta']}\n"
        )

        print("Sending to Arduino:", command.strip())

        # Send command

        pending_limits = new_limits.copy()

        ser.write(command.encode("utf-8"))
        ser.flush()

        settings_message.config(
            text="Waiting for Arduino confirmation...",
            fg="#c47a00"
        )

    except ValueError as e:

        settings_message.config(
            text=str(e),
            fg="red"
        )

    except serial.SerialException as e:

        pending_limits = None

        settings_message.config(
            text="Serial error: " + str(e),
            fg="red"
        )


ttk.Button(
    settings,
    text="Apply Thresholds",
    command=apply_limits
).grid(
    row=3,
    column=0,
    columnspan=6,
    pady=8
)

# ==========================================
# ALERT HISTORY
# ==========================================

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

history = tk.Listbox(
    history_frame,
    height=7,
    font=("Arial", 10)
)

history.pack(fill="both", expand=True)


def add_history(message):

    timestamp = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    history.insert(
        0,
        timestamp + " - " + message
    )

    if history.size() > 30:
        history.delete(30)


# ==========================================
# PROCESS SENSOR READINGS
# ==========================================

def process_reading(data):

    global last_message

    if "error" in data:

        alert_status.config(
            text="SENSOR ERROR: " + data["error"],
            fg="red"
        )

        return

    required = [
        "temperature",
        "humidity",
        "lux",
        "lowLight",
        "drasticChange"
    ]

    if not all(key in data for key in required):
        print("Incomplete sensor data:", data)
        return

    try:

        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        lux = float(data["lux"])

        low_light = data["lowLight"]
        drastic = data["drasticChange"]

    except (ValueError, TypeError):
        print("Invalid sensor data:", data)
        return

    # Update sensor cards

    temp_value.config(
        text=f"{temperature} °C"
    )

    hum_value.config(
        text=f"{humidity} %"
    )

    lux_value.config(
        text=f"{lux} lux"
    )

    # Light status

    if low_light:

        light_status.config(
            text="LOW LIGHT: Plant may need more light",
            fg="#c47a00"
        )

    else:

        light_status.config(
            text="Light level is within the configured range",
            fg="green"
        )

    # Check climate conditions

    problems = []

    if temperature < limits["temp_low"]:
        problems.append("Temperature too low")

    if temperature > limits["temp_high"]:
        problems.append("Temperature too high")

    if humidity < limits["hum_low"]:
        problems.append("Humidity too low")

    if humidity > limits["hum_high"]:
        problems.append("Humidity too high")

    if drastic:
        problems.append("Drastic change in light intensity")

    # Determine system status

    if problems:

        message = "WARNING: " + ", ".join(problems)

        alert_status.config(
            text=message,
            fg="red"
        )

        status = "ALERT"

    else:

        message = "All monitored conditions are within limits"

        alert_status.config(
            text=message,
            fg="green"
        )

        status = "NORMAL"

    # Record changed alerts

    if message != last_message:

        add_history(message)

        last_message = message

    # Save sensor readings

    with open(log_file, "a", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            temperature,
            humidity,
            lux,
            status
        ])


# ==========================================
# READ ARDUINO SERIAL DATA
# ==========================================

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

                # Successful threshold update

                if line == "ACK:LIMITS":

                    if pending_limits is not None:

                        limits.update(pending_limits)
                        pending_limits = None

                        settings_message.config(
                            text="Arduino confirmed: Thresholds updated!",
                            fg="green"
                        )

                    else:

                        print("Unexpected threshold acknowledgement")

                # Arduino rejected command

                elif line.startswith("ERROR:"):

                    pending_limits = None

                    settings_message.config(
                        text="Arduino rejected: " + line,
                        fg="red"
                    )

                # Normal JSON sensor readings

                else:

                    try:

                        data = json.loads(line)

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

            settings_message.config(
                text="Serial error: " + str(e),
                fg="red"
            )

            print("Serial error:", e)

    root.after(200, read_serial)


# ==========================================
# CLOSE APPLICATION
# ==========================================

def close_app():

    if ser and ser.is_open:
        ser.close()

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_app
)

# Start serial reading

read_serial()

root.mainloop()