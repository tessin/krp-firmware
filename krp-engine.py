import requests
import socket

#################################################################

class KrpController:

    baseUrl = "https://azfn-linqpad-web-app-e5opllzphjvwc.azurewebsites.net/api/krp"
    minimumMinutesBetweenLogs = 0
    users = []
    currentUser = 0;

    def __init__(self, client):
        self.client = client
        self.client.controller = self;

    def init(self):
        self.client.init()
        self.client.write(self.client.getIp(),"Loading...")
        url = f"{self.baseUrl}/config"
        response = requests.get(url=url)
        data = response.json()
        self.minimumMinutesBetweenLogs = data['MinimumMinutesBetweenLogs']
        for jUser in data['Users']:
            self.users.append(KrpPlayer(jUser['Id'], jUser['FirstName'], jUser['LastName']))
        self.client.clear()
        self.client.loop()

    def onLeft(self):
        self.client.write("left","")

    def onRight(self):
        self.client.write("right", "")

    def onOk(self):
        self.client.write("ok", "")

#################################################################

class KrpPlayer:

    def __init__(self, id, firstName, lastName):
        self.id = id,
        firstName = firstName,
        lastName = lastName

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
        return socket.gethostbyname(socket.gethostname())

class KrpConsoleClient(KrpClient):

    def init(self):
        pass

    def write(self, top16, bottom16):
        top16 = '{0: <16}'.format(top16[:16])
        bottom16 = '{0: <16}'.format(bottom16[:16])
        print("+----------------+")
        print("|"+top16+"|")
        print("+----------------+")
        print("|"+bottom16+"|")
        print("+----------------+")

    def loop(self):
        while True:
            key = input("")
            if key == "r":
                controller.onRight()
            if key == "l":
                controller.onLeft()
            if key == "o":
                controller.onOk()
            if key == "q":
                break

#################################################################

controller = KrpController(KrpConsoleClient())
controller.init()
#controller.start()
