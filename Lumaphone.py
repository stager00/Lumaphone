from picrawler import Picrawler
from robot_hat import TTS, Music, Ultrasonic
from bleak import BleakScanner
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
import time
import asyncio
import math

# Initialize components
crawler = Picrawler()
tts = TTS()
music = Music()
sonar = Ultrasonic(Pin("D2"), Pin("D3"))

# OLED display setup
serial = i2c(port=1, address=0x3C)
oled = ssd1306(serial)

# Bluetooth MAC address of your phone
phone_mac_address = "20:20:08:59:27:13"

# Function to find the phone
async def find_phone():
    devices = await BleakScanner.discover()
    return any(device.address == phone_mac_address for device in devices)

# Function to draw the circle and needle
def draw_needle(angle):
    with canvas(oled) as draw:
        center_x, center_y = 64, 32
        radius = 30
        # Draw circle
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), outline="white")
        # Draw needle
        end_x = center_x + int(radius * math.cos(math.radians(angle)))
        end_y = center_y + int(radius * math.sin(math.radians(angle)))
        draw.line((center_x, center_y, end_x, end_y), fill="white")

# Main function
async def main():
    speed = 80
    while True:
        try:
            phone_detected = await find_phone()
            if phone_detected:
                print("Phone detected! Moving towards it.")
                tts.say("Phone detected! Moving towards it.")
                draw_needle(0)  # Assuming 0 degrees for simplicity
                crawler.do_action('forward', 1, speed)
            else:
                print("Phone not detected. Scanning...")
                tts.say("Phone not detected. Scanning...")
                draw_needle(90)  # Assuming 90 degrees for simplicity
                crawler.do_action('turn left', 1, speed)
            
            # Obstacle avoidance
            distance = sonar.read()
            if distance > 0 and distance <= 15:
                print("Obstacle detected! Avoiding...")
                tts.say("Obstacle detected! Avoiding...")
                crawler.do_action('turn right', 1, speed)
            else:
                crawler.do_action('forward', 1, speed)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            tts.say("An error occurred.")
        time.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
