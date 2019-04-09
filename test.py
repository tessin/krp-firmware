import sys, termios, tty, os, time
from socket import *
from threading import Thread

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

button_delay = 0.2

OUR_ADDRESS     = ('127.0.0.1', 3003) # listen to
ADDRESS_TO_SEND = ('127.0.0.1', 3002) # send to
sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt( SOL_SOCKET,SO_REUSEADDR, 1 )
sock.bind( OUR_ADDRESS )
sock.setsockopt( SOL_SOCKET,SO_BROADCAST, 1 )

def run(*args):
    while True:
        data, addr = sock.recvfrom(256)
        data = data.decode("utf-8")
        print("+----------------+")
        print("|"+data[:16]+"|")
        print("+----------------+")
        print("|"+data[16:]+"|")
        print("+----------------+")

        char = getch()

        if (char == "p"):
            print("Stop!")
            exit(0)
        
        if (char == "a"):
            print("Left pressed")
            sock.sendto("LEFT".encode(), ADDRESS_TO_SEND)
            time.sleep(button_delay)

        if (char == "d"):
            print("Right pressed")
            sock.sendto("RIGHT".encode(), ADDRESS_TO_SEND)
            time.sleep(button_delay)

        if (char == "s"):
            print("OK pressed")
            sock.sendto("OK".encode(), ADDRESS_TO_SEND)
            time.sleep(button_delay)

Thread(target=run).start()
