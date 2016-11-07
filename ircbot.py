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


        #storing the parameters
        self.network = network
        self.port = port
        self.nick = nick
        self.channel = channel

        #defining commands that are static, can be added like examples as
        #command-answer. Commands are recognized as !command from irc
        self.commandDict = {
            "komento": "vastaus 1",
            "komento2": "vastaus2"
        }

        #connecting here
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
        #check for commands that are just answers from commandDict
        if self.data.find(("PRIVMSG " + self.channel + " :" + "!").encode()) != -1:
            strData = self.data.decode()
            dump, command = strData.split("PRIVMSG " + self.channel + " :" + "!", 1)
            command = command.strip()
            if command in self.commandDict:
                self.send(self.commandDict[command])
                self.consolePrint("command detected: !" + command)
                self.consolePrint("answered: " + self.commandDict[command])
        #topicchange (placeholder)
        if self.data.find(("PRIVMSG " + self.channel + " :!topic").encode()) != -1:
            self.topic()


    def send(self, message):
        #sends the parameter message to irc channel
        self.irc.send(('PRIVMSG '+self.channel + ' :' + str(message) + '\r\n').encode())


    def topic(self):
        self.irc.send(('TOPIC '+self.channel + '\r\n').encode())
        self.data = self.irc.recv (4096)
        if self.data.find((" testibot " + self.channel + " :").encode()) != -1:
            strData = self.data.decode()  #str(self.data)
            startString = self.nick + " " + self.channel + " :"
            endString = ":"

            dump, topicStartCutted =  strData.split(startString, 1)
            topic, dump = topicStartCutted.split(endString, 1)
            self.consolePrint("Current topic is: " + topic)

            if topic.startswith("OFF"): #changing from OFF to ON
                newTopic = "ON" + topic[3:]
                self.setTopic(newTopic)
            elif topic.startswith("ON"): #changing from ON to OFF
                newTopic = "OFF" + topic[2:]
                self.setTopic(newTopic)
            else:
                self.consolePrint("topic is weird")


    def setTopic(self, topic = ""):
        self.irc.send(("TOPIC " + self.channel + " :" + topic + '\r\n').encode())
        if topic:
            self.consolePrint("Attempting to set new topic as: " + topic)
    def consolePrint(self, text):
        #prints stuff in a "clean" manner
        output = "["+  time.strftime("%H:%M") + "] " + text
        print(output)



#just example parametes
botti = ircBot("open.ircnet.net", 6667, "testibot", "#ircbottesti")





def main():
    while True:
        botti.recieve()
        #time.sleep(0.1)



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