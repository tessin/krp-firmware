import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

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

led_pin = 20
GPIO.setup(led_pin, GPIO.OUT)

left_button_pin = 13
GPIO.setup(left_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ok_button_pin = 19
GPIO.setup(ok_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

right_button_pin = 26
GPIO.setup(right_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# while True:
#     GPIO.output(led_pin, GPIO.HIGH)
#     print("hello")
#     time.sleep(2)
#     GPIO.output(led_pin, GPIO.LOW)
#     time.sleep(2)

while True:
    input_state = GPIO.input(ok_button_pin)
    if input_state == False:
        print('OK Button Pressed')
        time.sleep(0.2)







