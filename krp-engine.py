import requests
from socket import *
from threading import Thread, Timer

#################################################################

# Last cleaned by:
# Niels

class KrpController:

    baseUrl = "https://azfn-linqpad-web-app-e5opllzphjvwc.azurewebsites.net/api/krp"
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
        self.client.write(self.client.getIp(),"Loading...")
        url = self.baseUrl + "/config"
        response = requests.get(url=url)
        data = response.json()
        print(str(data))
        self.minimumMinutesBetweenLogs = data['MinimumMinutesBetweenLogs']
        for jUser in data['Users']:
            self.users.append(KrpPlayer(jUser['Id'], jUser['FirstName'], jUser['LastName']))

        self.client.clear()
        self.__writeLastCleanedBy()
        # self.client.loop()

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
        self.client.write("Registering...", "")

        self.__cancelReturningTimer()

        try:
            url = self.baseUrl + "/log?playerId=" + userId
            requests.get(url=url)
            self.latestLogByUserId = userId
            self.__writeLastCleanedBy()
        except:
            self.__writeError("")
            pass
    
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
        return gethostbyname(gethostname())

OUR_ADDRESS     = ('127.0.0.1', 3002) # listen to
ADDRESS_TO_SEND = ('127.0.0.1', 3003) # send to

class KrpConsoleClient(KrpClient):
    sock = None

    def init(self):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt( SOL_SOCKET,SO_REUSEADDR, 1 )
        self.sock.bind( OUR_ADDRESS )
        self.sock.setsockopt( SOL_SOCKET,SO_BROADCAST, 1 )

        def buttonHandler(*args):
            while True:
                try:
                    data, addr = sock.recvfrom(256)
                    button = data.decode("utf-8")
                    print(button)
                    controller.onButtonPress(button)
                except:
                    pass

        Thread(target=buttonHandler).start()

    def write(self, top16, bottom16):
        top16 = '{0: <16}'.format(top16[:16])
        bottom16 = '{0: <16}'.format(bottom16[:16])
        self.sock.sendto((top16 + bottom16).encode(), ADDRESS_TO_SEND)
        print("+----------------+")
        print("|"+top16+"|")
        print("+----------------+")
        print("|"+bottom16+"|")
        print("+----------------+")

#################################################################

controller = KrpController(KrpConsoleClient())
controller.init()
