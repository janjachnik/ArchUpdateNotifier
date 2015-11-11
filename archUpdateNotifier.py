import sys
from PyQt4 import QtGui
import subprocess

# Arch update tray icon using Qt
#
# Left-click - shows notification (doesn't update cache)
# Right-click - shows menu
# Config file to set auto check interval (0 means never) (or argparse)
# Pacman for system updates
# Yaourt for AUR updates

#TODO add error checking on system calls

def getAURUpdates():
    command = "yaourt -Qua"
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout
    updates = []
    for line in output:
        text = line.decode("utf-8").replace('\n','')
        name = text.split(' ')[0]
        # remove "aur/"
        update = name.split('/')[1]
        updates.append(update)
    return updates
    
def getSystemUpdates():
    command = "checkupdates"
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout
    updates = []
    for line in output:
        updates.append(line.decode("utf-8").replace('\n', ''))
    return updates
    
def formatData(updates):
    if len(updates)==0:
        return "Up to date!"
    formatted = ""
    for update in updates:
        formatted += update + "\n"        
    return formatted
    

class SystemTrayUpdateNotifier():
    def __init__(self, parent=None):
        self.app = QtGui.QApplication(sys.argv)
        self.style = self.app.style()
        self.icon = QtGui.QIcon(self.style.standardPixmap(QtGui.QStyle.SP_FileIcon))
        self.trayIcon = QtGui.QSystemTrayIcon(self.icon, parent)
        self.menu = QtGui.QMenu(parent)

        checkAction = self.menu.addAction("Check for updates", self.checkForUpdates)
        self.menu.addAction("Display updates", self.displayUpdates)
        exitAction = self.menu.addAction("Exit", self.app.quit)
        
        self.trayIcon.setContextMenu(self.menu)
        self.trayIcon.show()
        self.trayIcon.activated.connect(self.clickHandler)
        
        self.checkForUpdates()
        
        sys.exit(self.app.exec_())
        
    def checkForUpdates(self):
        self.system_updates = getSystemUpdates()
        self.aur_updates = getAURUpdates()
        #self.lastChecked = time.now()
        self.setTooltip()
        
    def setTooltip(self):
        minutes = 0
        tooltip = "Last checked " + str(minutes) + "minutes ago."
        self.trayIcon.setToolTip(tooltip)
        
    def displayUpdates(self):
        print(formatData(self.system_updates))
        print(formatData(self.aur_updates))
        
    def clickHandler(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.displayUpdates()
        
 
   

def main():
    updater = SystemTrayUpdateNotifier()

if __name__ == '__main__':
    main()
