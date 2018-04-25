import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# lcd_rs = 25
# lcd_en = 24
# lcd_d4 = 23
# lcd_d5 = 17
# lcd_d6 = 18
# lcd_d7 = 22
# lcd_backlight = 4
# lcd_columns = 16
# lcd_rows = 2
#
# lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
#
# lcd.home()
# lcd.clear()
# lcd.message("HelloWorld!")

status_led = 21

GPIO.setup(status_led, GPIO.OUT)

while True:
    GPIO.output(status_led, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(status_led, GPIO.LOW)
    time.sleep(2)