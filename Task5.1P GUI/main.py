#CODE FOR GUI ONLY , i have made it seperate to test it and show the GUI window in the video
import tkinter as tk

def change_room():
    room = selected_room.get()

    print("Selected:", room)


def exit_program():
    window.destroy()


window = tk.Tk()
window.title("Home Lighting Control")
window.geometry("450x350")

tk.Label(
    window,
    text="Home Lighting Control",
    font=("Arial", 22, "bold")
).pack(pady=20)

tk.Label(
    window,
    text="Select a room:",
    font=("Arial", 14)
).pack(pady=10)

selected_room = tk.StringVar()

tk.Radiobutton(
    window,
    text="Living Room",
    variable=selected_room,
    value="Living Room",
    command=change_room,
    font=("Arial", 15)
).pack()

tk.Radiobutton(
    window,
    text="Bathroom",
    variable=selected_room,
    value="Bathroom",
    command=change_room,
    font=("Arial", 15)
).pack()

tk.Radiobutton(
    window,
    text="Closet",
    variable=selected_room,
    value="Closet",
    command=change_room,
    font=("Arial", 15)
).pack()

tk.Button(
    window,
    text="Exit",
    command=exit_program,
    width=10
).pack(pady=25)

window.mainloop()



###                                 *CODE FOR WHOLE SETUP*

# import tkinter as tk
# import RPi.GPIO as GPIO

# # ---------------- GPIO SETUP ----------------

# GPIO.setmode(GPIO.BCM)

# LIVING_ROOM = 17
# BATHROOM = 27
# CLOSET = 22

# GPIO.setup(LIVING_ROOM, GPIO.OUT)
# GPIO.setup(BATHROOM, GPIO.OUT)
# GPIO.setup(CLOSET, GPIO.OUT)

# # Start with all LEDs OFF
# GPIO.output(LIVING_ROOM, GPIO.LOW)
# GPIO.output(BATHROOM, GPIO.LOW)
# GPIO.output(CLOSET, GPIO.LOW)


# # ---------------- LED CONTROL ----------------

# def change_room():
#     room = selected_room.get()

#     # Turn all LEDs OFF first
#     GPIO.output(LIVING_ROOM, GPIO.LOW)
#     GPIO.output(BATHROOM, GPIO.LOW)
#     GPIO.output(CLOSET, GPIO.LOW)

#     # Turn ON the selected room's LED
#     if room == "Living Room":
#         GPIO.output(LIVING_ROOM, GPIO.HIGH)

#     elif room == "Bathroom":
#         GPIO.output(BATHROOM, GPIO.HIGH)

#     elif room == "Closet":
#         GPIO.output(CLOSET, GPIO.HIGH)


# # ---------------- EXIT FUNCTION ----------------

# def exit_program():
#     GPIO.output(LIVING_ROOM, GPIO.LOW)
#     GPIO.output(BATHROOM, GPIO.LOW)
#     GPIO.output(CLOSET, GPIO.LOW)

#     GPIO.cleanup()
#     window.destroy()


# # ---------------- GUI ----------------

# window = tk.Tk()
# window.title("Home Lighting Control")
# window.geometry("450x350")

# title = tk.Label(
#     window,
#     text="Home Lighting Control",
#     font=("Arial", 22, "bold")
# )

# title.pack(pady=20)

# instruction = tk.Label(
#     window,
#     text="Select a room to turn on its light:",
#     font=("Arial", 14)
# )

# instruction.pack(pady=10)


# # Radio button variable
# selected_room = tk.StringVar()
# selected_room.set("")


# # Living Room
# living_button = tk.Radiobutton(
#     window,
#     text="Living Room",
#     variable=selected_room,
#     value="Living Room",
#     command=change_room,
#     font=("Arial", 15)
# )

# living_button.pack(anchor="w", padx=100, pady=5)


# # Bathroom
# bathroom_button = tk.Radiobutton(
#     window,
#     text="Bathroom",
#     variable=selected_room,
#     value="Bathroom",
#     command=change_room,
#     font=("Arial", 15)
# )

# bathroom_button.pack(anchor="w", padx=100, pady=5)


# # Closet
# closet_button = tk.Radiobutton(
#     window,
#     text="Closet",
#     variable=selected_room,
#     value="Closet",
#     command=change_room,
#     font=("Arial", 15)
# )

# closet_button.pack(anchor="w", padx=100, pady=5)


# # Exit button
# exit_button = tk.Button(
#     window,
#     text="Exit",
#     command=exit_program,
#     font=("Arial", 14),
#     width=10
# )

# exit_button.pack(pady=25)


# # ---------------- START GUI ----------------

# window.mainloop()
