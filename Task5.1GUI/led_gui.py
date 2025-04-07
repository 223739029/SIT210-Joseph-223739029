import RPi.GPIO as GPIO
from tkinter import *

GPIO.setmode(GPIO.BCM)
LED_PINS = {'Red':17,'Green':27,'Blue':22}

for pin in LED_PINS.values():
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)

def turn_on_led():
	selected = led_var.get()
	for colour, pin in LED_PINS.items():
		GPIO.output(pin, GPIO.HIGH if colour == selected else GPIO.LOW)

def exit_gui():
	GPIO.cleanup()
	root.destroy()

root = Tk()
root.title("LED GUI")
root.geometry("300x200")

led_var = StringVar()
led_var.set("Red")

Label(root, text="Select which LED to turn on:", font=("Arial", 14)).pack(pady=10)

for color in LED_PINS.keys():
	Radiobutton(root, text=color, variable=led_var, value=color, command=turn_on_led, font=("Arial", 12)).pack(anchor=W, padx=20)

Button(root, text="EXIT", command=exit_gui, fg="white", bg="red").pack(pady=10)

root.mainloop()
