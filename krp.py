import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
from time import sleep
import commands
from threading import Thread, Timer
import requests
from socket import *
import sys, termios, tty, os, logging

handler = logging.FileHandler('errors.log')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logger.info('\n------------------------------------')


GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 4
lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

lcd.home()
lcd.clear()

lcd.message(commands.getoutput('hostname -I'))
sleep(5)

lcd.home()
lcd.clear()

lcd.message("HelloWorld!\nFoo")

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

# GPIO.output(led_pin, GPIO.HIGH)

#while True:
#    input_state = GPIO.input(ok_button_pin)
#    if input_state == False:
#        print('OK Button Pressed')
#        time.sleep(0.2)

class KrpController:

    baseUrl = "http://azfn-linqpad-web-app-e5opllzphjvwc.azurewebsites.net/api/krp"
    minimumMinutesBetweenLogs = 0
    users = []
    latestLogByUserId = None #todo: get this from the server
    selectedUserIndex = 0

    returnTimer = None

    def __init__(self, client):
        self.client = client
        self.client.controller = self

    def init(self):
        self.state = "LOADING"
        self.client.init()
        self.client.turnLed(True)

        ip = self.client.getIp()
        self.client.write(ip, "Loading...")
        url = self.baseUrl + "/config"

        try:
            response = requests.get(url=url)
            data = response.json()
            # print(str(data))
            self.minimumMinutesBetweenLogs = data['MinimumMinutesBetweenLogs']
            for jUser in data['Users']:
                self.users.append(KrpPlayer(jUser['Id'], jUser['FirstName'], jUser['LastName']))

            self.latestLogByUserId = data['LatestLogByUserId']

            self.client.clear()
            self.__writeLastCleanedBy()
        except:
            logger.info(sys.exc_info()[0])
            print(sys.exc_info()[0])

    def onButtonPress(self, button):            # handler for button press
        if self.state == "MENU":
            self.__selectPlayer()
        elif self.state == "SELECT_PLAYER":
            if button == "LEFT":
                self.selectedUserIndex -= 1
                if self.selectedUserIndex == -1: self.selectedUserIndex = len(self.users) - 1
                self.__selectPlayer()
            elif button == "RIGHT":
                self.selectedUserIndex += 1
                if self.selectedUserIndex == len(self.users): self.selectedUserIndex = 0
                self.__selectPlayer()
            elif button == "OK":
                self.__registerPlayer(self.users[self.selectedUserIndex].id)
        elif self.state == "ERROR":
            self.__writeLastCleanedBy()

    def __writeLastCleanedBy(self):             # Show main menu
        self.state = "MENU"
        user = self.__findUserById(self.latestLogByUserId)
        self.client.write("Last cleaned by:", user.firstName if user is not None else "<NONE>")

        self.__cancelReturningTimer()

    def __selectPlayer(self):                   # Show select player on led
        self.state = "SELECT_PLAYER"
        user = self.users[self.selectedUserIndex]

        self.__startReturningTimer()
        
        userString = str(user).ljust(14)
        self.client.write("SELECT", "<" + userString + ">")

    def __registerPlayer(self, userId):         # Show registing player on led
        self.state = "REGISTERING"
        self.client.turnLed(True)
        self.client.write("Registering...", "")

        self.__cancelReturningTimer()

        try:
            url = self.baseUrl + "/log?playerId=" + str(userId)
            requests.get(url=url)
            self.latestLogByUserId = userId
            self.__writeLastCleanedBy()
        except:
            self.__writeError("")
            pass
        
        self.client.turnLed(False)
    
    def __writeError(self, error):              # Show Error on Led when register failed
        self.state = "ERROR"
        self.client.write("Oops!", error)
        self.__startReturningTimer()

    def __findUserById(self, userId):           # Find user by userId
        if userId is None:
            return None
        for user in self.users:
            if user.id == userId:
                return user
        return None
    
    def __startReturningTimer(self):            # Timer for returning to main menu when no signal in 5 seconds.
        self.__cancelReturningTimer()
        self.returnTimer = Timer(5, self.__writeLastCleanedBy)
        self.returnTimer.start()
    
    def __cancelReturningTimer(self):           # Cancel returing timer
        if self.returnTimer != None and self.returnTimer.is_alive():
            self.returnTimer.cancel()


#################################################################

class KrpPlayer:

    def __init__(self, id, firstName, lastName):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
    
    def __str__(self):
        return self.firstName

#################################################################

class KrpClient:
    controller = None

    def init(self):
        pass

    def write(self,top16,bottom16):
        pass

    def clear(self):
        self.write("","")

    def loop(self):
        pass

    def getIp(self):
        return '10.1.0.15'

class KrpConsoleClient(KrpClient):
    lcd = None

    def __init__(self, lcd):
        self.lcd = lcd

    def write(self, top16, bottom16):
        top16 = '{0: <16}'.format(top16[:16])
        bottom16 = '{0: <16}'.format(bottom16[:16])
        self.lcd.clear()
        self.lcd.message(top16 + "\n" + bottom16)
        print("+----------------+")
        print("|"+top16+"|")
        print("+----------------+")
        print("|"+bottom16+"|")
        print("+----------------+")
    
    def turnLed(self, on):
        if on:
            GPIO.output(led_pin, GPIO.HIGH)
        else:
            GPIO.output(led_pin, GPIO.LOW)
    
    def clear(self):
        self.lcd.clear()
        GPIO.output(led_pin, GPIO.LOW)

#################################################################

controller = KrpController(KrpConsoleClient(lcd))
controller.init()

def buttonPressed(button):
    controller.onButtonPress(button)
    print(button)

GPIO.add_event_detect(left_button_pin, GPIO.FALLING, callback=lambda x: buttonPressed("LEFT"), bouncetime=200)
GPIO.add_event_detect(ok_button_pin, GPIO.FALLING, callback=lambda x: buttonPressed("OK"), bouncetime=200)
GPIO.add_event_detect(right_button_pin, GPIO.FALLING, callback=lambda x: buttonPressed("RIGHT"), bouncetime=200)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def run(*args):
    while True:
		char = getch()

		if (char == "p"):
			print("Stop!")
			exit(0)

Thread(target=run).start()

# try:
#     while True:
#         sleep(1)
# except KeyboardInterrupt:
#     GPIO.cleanup()
