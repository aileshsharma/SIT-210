import tkinter as tk
import RPi.GPIO as GPIO

# ---------------- GPIO SETUP ----------------

# Set the GPIO numbering mode to BCM.
# This means the GPIO pins are identified by their BCM GPIO numbers.
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins connected to each room's LED.
LIVING_ROOM = 17
BATHROOM = 27
CLOSET = 22

# Configure the three GPIO pins as output pins.
GPIO.setup(LIVING_ROOM, GPIO.OUT)
GPIO.setup(BATHROOM, GPIO.OUT)
GPIO.setup(CLOSET, GPIO.OUT)

# Start with all LEDs turned OFF.
GPIO.output(LIVING_ROOM, GPIO.LOW)
GPIO.output(BATHROOM, GPIO.LOW)
GPIO.output(CLOSET, GPIO.LOW)


# ---------------- LED CONTROL ----------------

# This function is called whenever the user selects a room.
def change_room():
    # Get the room selected by the user from the GUI.
    room = selected_room.get()

    # Turn all LEDs OFF first.
    # This ensures that only the selected room's light remains ON.
    GPIO.output(LIVING_ROOM, GPIO.LOW)
    GPIO.output(BATHROOM, GPIO.LOW)
    GPIO.output(CLOSET, GPIO.LOW)

    # Turn ON the LED corresponding to the selected room.
    if room == "Living Room":
        GPIO.output(LIVING_ROOM, GPIO.HIGH)

    elif room == "Bathroom":
        GPIO.output(BATHROOM, GPIO.HIGH)

    elif room == "Closet":
        GPIO.output(CLOSET, GPIO.HIGH)


# ---------------- EXIT FUNCTION ----------------

# This function is called when the user presses the Exit button.
def exit_program():
    # Turn all LEDs OFF before closing the program.
    GPIO.output(LIVING_ROOM, GPIO.LOW)
    GPIO.output(BATHROOM, GPIO.LOW)
    GPIO.output(CLOSET, GPIO.LOW)

    # Reset the GPIO pins and release them for safe use.
    GPIO.cleanup()

    # Close the GUI window.
    window.destroy()


# ---------------- GUI ----------------

# Create the main Tkinter window.
window = tk.Tk()

# Set the title displayed at the top of the window.
window.title("Home Lighting Control")

# Set the size of the GUI window.
window.geometry("450x350")


# Create the main title displayed in the GUI.
title = tk.Label(
    window,
    text="Home Lighting Control",
    font=("Arial", 22, "bold")
)

# Display the title with vertical spacing.
title.pack(pady=20)


# Create an instruction label telling the user what to do.
instruction = tk.Label(
    window,
    text="Select a room to turn on its light:",
    font=("Arial", 14)
)

# Display the instruction below the title.
instruction.pack(pady=10)


# Create a StringVar to store the room selected by the user.
selected_room = tk.StringVar()

# Initially, no room is selected.
selected_room.set("")


# ---------------- LIVING ROOM BUTTON ----------------

# Create a radio button for the Living Room.
# Selecting it stores "Living Room" in selected_room
# and calls the change_room() function.
living_button = tk.Radiobutton(
    window,
    text="Living Room",
    variable=selected_room,
    value="Living Room",
    command=change_room,
    font=("Arial", 15)
)

# Display the Living Room radio button.
living_button.pack(anchor="w", padx=100, pady=5)


# ---------------- BATHROOM BUTTON ----------------

# Create a radio button for the Bathroom.
# Selecting it stores "Bathroom" in selected_room
# and calls the change_room() function.
bathroom_button = tk.Radiobutton(
    window,
    text="Bathroom",
    variable=selected_room,
    value="Bathroom",
    command=change_room,
    font=("Arial", 15)
)

# Display the Bathroom radio button.
bathroom_button.pack(anchor="w", padx=100, pady=5)


# ---------------- CLOSET BUTTON ----------------

# Create a radio button for the Closet.
# Selecting it stores "Closet" in selected_room
# and calls the change_room() function.
closet_button = tk.Radiobutton(
    window,
    text="Closet",
    variable=selected_room,
    value="Closet",
    command=change_room,
    font=("Arial", 15)
)

# Display the Closet radio button.
closet_button.pack(anchor="w", padx=100, pady=5)


# ---------------- EXIT BUTTON ----------------

# Create an Exit button that calls exit_program()
# when the user clicks it.
exit_button = tk.Button(
    window,
    text="Exit",
    command=exit_program,
    font=("Arial", 14),
    width=10
)

# Display the Exit button with vertical spacing.
exit_button.pack(pady=25)


# ---------------- START GUI ----------------

# Start the Tkinter event loop.
# This keeps the GUI running and waits for user interactions.
window.mainloop()
