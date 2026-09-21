# Import Tkinter for creating the graphical user interface
import tkinter as tk

# Import PWMLED to control the LED brightness using PWM
from gpiozero import PWMLED


# ---------------------------------------------------------
# LED SETUP
# ---------------------------------------------------------

# The LED is connected to GPIO 18 of the Raspberry Pi.
# GPIO 18 supports PWM, which allows the brightness
# of the LED to be controlled.
led = PWMLED(18)


# ---------------------------------------------------------
# BRIGHTNESS CONTROL FUNCTION
# ---------------------------------------------------------

# This function is called whenever the user moves
# the brightness slider.
def change_brightness(value):

    # The slider gives a value between 0 and 100.
    # We divide by 100 to convert it to a value
    # between 0.0 and 1.0 for PWM.
    brightness = float(value) / 100

    # Set the PWM value of the LED.
    # 0.0 means OFF and 1.0 means maximum brightness.
    led.value = brightness


# ---------------------------------------------------------
# ON BUTTON FUNCTION
# ---------------------------------------------------------

# This function is executed when the ON button is pressed.
def turn_on():

    # Move the slider to 100%.
    # This also triggers the brightness function
    # and sets the LED to maximum brightness.
    brightness_slider.set(100)


# ---------------------------------------------------------
# OFF BUTTON FUNCTION
# ---------------------------------------------------------

# This function is executed when the OFF button is pressed.
def turn_off():

    # Move the slider to 0%.
    # This sets the LED brightness to zero.
    brightness_slider.set(0)


# ---------------------------------------------------------
# EXIT FUNCTION
# ---------------------------------------------------------

# This function is executed when the Exit button is pressed.
def exit_program():

    # Turn the LED off before closing the program.
    led.off()

    # Close the GUI window.
    window.destroy()


# ---------------------------------------------------------
# CREATE THE GUI WINDOW
# ---------------------------------------------------------

# Create the main Tkinter window.
window = tk.Tk()

# Set the title displayed at the top of the window.
window.title("Living Room Light Control")

# Set the size of the GUI window.
window.geometry("450x350")


# ---------------------------------------------------------
# GUI TITLE
# ---------------------------------------------------------

# Create a label to display the application title.
title = tk.Label(
    window,
    text="Living Room Light Control",
    font=("Arial", 20)
)

# Display the title with some vertical spacing.
title.pack(pady=20)


# ---------------------------------------------------------
# BRIGHTNESS LABEL
# ---------------------------------------------------------

# Create a label that tells the user what
# the slider is controlling.
brightness_label = tk.Label(
    window,
    text="Brightness"
)

# Display the brightness label.
brightness_label.pack()


# ---------------------------------------------------------
# BRIGHTNESS SLIDER
# ---------------------------------------------------------

# Create a horizontal slider for controlling
# the LED brightness.
brightness_slider = tk.Scale(
    window,

    # Minimum slider value is 0%.
    from_=0,

    # Maximum slider value is 100%.
    to=100,

    # Make the slider horizontal.
    orient=tk.HORIZONTAL,

    # Set the length of the slider.
    length=300,

    # Call change_brightness whenever
    # the slider value changes.
    command=change_brightness
)

# Set the initial brightness to 0%.
brightness_slider.set(0)

# Display the slider with some spacing.
brightness_slider.pack(pady=20)


# ---------------------------------------------------------
# ON BUTTON
# ---------------------------------------------------------

# Create the ON button.
on_button = tk.Button(
    window,
    text="ON",
    width=10,

    # When pressed, call the turn_on function.
    command=turn_on
)

# Display the ON button.
on_button.pack(pady=5)


# ---------------------------------------------------------
# OFF BUTTON
# ---------------------------------------------------------

# Create the OFF button.
off_button = tk.Button(
    window,
    text="OFF",
    width=10,

    # When pressed, call the turn_off function.
    command=turn_off
)

# Display the OFF button.
off_button.pack(pady=5)


# ---------------------------------------------------------
# EXIT BUTTON
# ---------------------------------------------------------

# Create the Exit button.
exit_button = tk.Button(
    window,
    text="Exit",
    width=10,

    # When pressed, call the exit_program function.
    command=exit_program
)

# Display the Exit button.
exit_button.pack(pady=10)


# ---------------------------------------------------------
# START THE GUI
# ---------------------------------------------------------

# Keep the GUI running and wait for user interaction.
# The program responds to actions such as moving
# the slider or pressing a button.
window.mainloop()