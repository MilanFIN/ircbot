'''
***************************************
Copyright Milan Mäkipää 2016
This should at some point act as a simple
bot for IRCnet channels
***************************************
'''



#import psutil
import socket
import time





class ircBot():
    def __init__(self, network, port, nick, channel):

        self.network = network
        self.port = port
        self.nick = nick
        self.channel = channel


        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((network.encode(), port)) # normally port=6667
        self.data = self.irc.recv (4096)
        self.irc.send(("USER " + nick + " " + nick +" " + nick + " :python_based_bot!\r\n").encode())
        self.irc.send(("NICK " + nick + "\r\n").encode())
        self.irc.send(("JOIN " + channel + "\r\n").encode())

        self.consolePrint("connected")
    def recieve(self):
        #must be called periodically, otherwice server will cut connection
        try:
            self.data = self.irc.recv (4096)
        except ConnectionAbortedError:
            self.data = "".encode()
        #keepalive, must answer pong if ping is recieved.
        if self.data.find('PING'.encode()) != -1:
            self.irc.send(('PONG ' + str(self.data.split()[1]) + '\r\n').encode())
        #check for commands
        if self.data.find(("PRIVMSG " + self.channel + " :!komento").encode()) != -1:
            self.send("vastaus")
            self.consolePrint("!komento noticed, answered")

    def send(self, message):
        #sends the parameter message to irc channel
        self.irc.send(('PRIVMSG '+self.channel + ' ' + str(message) + '\r\n').encode())

    def consolePrint(self, text):
        #prints stuff in a "clean" manner
        output = "[" + time.strftime("%d-%m-%Y | %H:%M:%S") + "] " + text
        print(output)



#just example parametes
botti = ircBot("irc.cc.tut.fi", 6667, "testibot", "#ircbottesti")

def main():
    while True:
        botti.recieve()
        time.sleep(0.1)


if __name__ == "__main__":
    main()




#to be added later. A method that checks if a specific process is running
'''

    if data.find('!softa'.encode()) !=-1:
        print("lahetys")
        x = "none"
        for i in (psutil.pids()):
            x = psutil.Process(i).name()
            break
'''