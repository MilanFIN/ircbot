'''
***************************************
Copyright MilanFIN 2017
This should at some point act as a simple
bot for IRCnet channels
***************************************
'''




import socket
import time
import re
import datetime



class ircBot():
    def __init__(self, network, port, nick, realName, channel):

        #storing the parameters for connecting to server
        self.network = network
        self.port = port
        self.nick = nick
        self.channel = channel
        self.realName = realName
        #name of the process that runs on the host computer, ircbot can check
        #if it is running
        self.processName = "firefox.exe"
        self.processStatus = False

        #store current hour of the day, needed for hourly actions
        self.previouosHour = time.strftime("%H")
        #defining commands that are static, can be added like examples as
        #"command": "answer". Commands are recognized as !command from irc
        self.commandDict = {
            "komento": "vastaus 1",
            "komento2": "vastaus2"
        }
        self.userDict = {}
        self.currentUsers = []

        #connecting here
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((network.encode(), port)) # normally port=6667
        self.data = self.irc.recv (4096)
        self.irc.send(("USER " + nick + " " + nick +" " + nick + " :" + self.realName + "\r\n").encode())
        self.irc.send(("NICK " + nick + "\r\n").encode())
        self.irc.send(("JOIN " + channel + "\r\n").encode())

        self.consolePrint("connected")


        self.readFile()
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
            if command == "uptime":
                self.upTime()
        if self.data.decode().find(("JOIN :" + self.channel)) != -1:
            self.newJoiner()
        #update user statistics file every hour change
        if time.strftime("%H") != self.previouosHour:
                self.previousHour = time.strftime("%H")
                self.fetchUsers()
                self.updateUserDict()
                self.writeFile()


    def send(self, message):
        #sends the parameter message to irc channel
        self.irc.send(('PRIVMSG '+self.channel + ' :' + str(message) + '\r\n').encode())
    def sendCommand(self, command):
        #sends commands, call without /, ex. /who -> who
        self.irc.send((command.capitalize() +" "+self.channel+ "\r\n").encode())
    def newJoiner(self):
        joinedNick = re.search(r'(:)(.+)(!)', self.data.decode())
        try:
            if joinedNick.group(2) != self.nick:
                messageEnding = ""
                if joinedNick.group(2) in self.userDict:
                    messageEnding = ". This nick has been seen here for " + str(self.userDict[joinedNick.group(2)]) + "hours."
                self.send("Welcome " + joinedNick.group(2) + messageEnding)
                self.consolePrint("greeted new user: " + joinedNick.group(2))
        except Exception:
            pass
    def consolePrint(self, text):
        #prints stuff in a "clean" manner
        output = "["+  time.strftime("%H:%M") + "] " + text
        print(output)

    def fetchUsers(self):
        ##gets list of nicks currently in the channel and puts them in
        #self.currentUsers
        self.currentUsers.clear()
        self.sendCommand("names")
        userData = self.irc.recv (4096).decode()
        splitData = []
        splitData = userData.split("\n")
        #print(splitData)
        for i in splitData:
            #print(i)
            if i.find(" :End of NAMES list.") != -1:
                break
            beg = i.find(self.channel + " :") + len(self.channel) + 2
            while True:
                end = i.find(" ", beg+1)
                if (end == -1):
                    break
                foundUser = i[beg:end].replace("@","").replace("+","")
                self.currentUsers.append(foundUser)
                beg = end+1
        #print(self.currentUsers)
        self.consolePrint("fetched current users of the channel")

    def updateUserDict(self):
        ##updates self.userDict with the info in self.currentUsers
        #adds 1, if nick is in currentUsers,sets value to 0 if new nick
        for i in self.currentUsers:
            if (i in self.userDict):
                self.userDict[i] += 1
            else:
                self.userDict[i] = 0
        self.consolePrint("updated channel user stats")
    def readFile(self):
        #reads the userfile to userDict, should be run in startup
        userFile = open("users.txt", "r")
        while True:
            user = userFile.readline().strip("\n")
            if not user: break
            if (user.startswith("#")): continue
            hoursFound = False
            while True:
                hours = userFile.readline().strip("\n")
                if (hours.startswith("#")):
                    continue
                if hours:
                    hoursFound = True
                break;
            if not hoursFound: break;
            if (hours.isdigit()):
                self.userDict[user] = int(hours)
        userFile.close()
        self.consolePrint("loaded user stats")
    def writeFile(self):
        #writes userDict values to file, fetchUsers should be called before
        #this, as it updates the dict contents to match current channel users
        userFile = open("users.txt", "w")
        for user, hours in self.userDict.items():
            userFile.write(user + "\n")
            userFile.write(str(hours) + "\n")
        userFile.close()
        self.consolePrint("saved user stats to file")
    def upTime(self):
        uptime = 0.0
        with open('/proc/uptime', 'r') as uptimeFile:
            seconds = float(uptimeFile.readline().split()[0])
            uptime = seconds/(3600*24)#str(timedelta(seconds = uptime_seconds))
        ##processUptime = datetime.now() - self.starTime
        self.send("Host system uptime is " + str(round(uptime, 2)) + " days")
        self.consolePrint("sent uptime to channel")


#just example parametes

#give ircBot parameters as: network, port, nick, realname, channel
#port is int, rest are string
botti0 = ircBot("irc.atw-inter.net", 6667, "testibot___", "python_bot", "#omairctesti")
#botti = ircBot("open.ircnet.net", 6667, "testibot", "#omairctesti")


def main():
    while True:
        botti0.recieve()

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