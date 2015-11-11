import sys
from PyQt4 import QtGui, QtCore
import subprocess

# Arch update tray icon using Qt
#
# Left-click - shows notification (doesn't update cache)
# Right-click - shows menu
# Config file to set auto check interval (0 means never) (or argparse)
# Pacman for system updates
# Yaourt for AUR updates

update_check_interval_minutes = 120

def getAURUpdates():
    command = "yaourt -Qua"
    try:
        output = subprocess.check_output(command,shell=True).decode("utf-8").split('\n')
    except subprocess.CalledProcessError as e:
        print(e.cmd, "exited with non-zero exit code: ", e.returncode, file=sys.stderr)
        return []
    updates = []
    for line in output:
        if line!='':
            updates.append(line.split(' ')[0].split('/')[1])
    return updates
    
def getSystemUpdates():
    command = "checkupdates"
    try:
        output = subprocess.check_output(command,shell=True).decode("utf-8").split('\n')
    except subprocess.CalledProcessError as e:
        print(e.cmd, "exited with non-zero exit code: ", e.returncode, file=sys.stderr)
        return []
    updates = []
    for line in output:
        if line!='':
            updates.append(line)
    return updates
    
def formatData(updates):
    if len(updates)==0:
        return "Up to date!"
    formatted = ""
    for update in updates:
        formatted += "  " + update + "\n"        
    return formatted
    

class SystemTrayUpdateNotifier():
    def __init__(self, parent=None):
        self.app = QtGui.QApplication(sys.argv)
        self.style = self.app.style()
        self.icon = QtGui.QIcon(self.style.standardPixmap(QtGui.QStyle.SP_FileIcon))
        self.trayIcon = QtGui.QSystemTrayIcon(self.icon, parent)
        
        # Build menu
        self.menu = QtGui.QMenu(parent)
        self.menu.addAction("Check for updates", self.checkForUpdates)
        self.menu.addAction("Exit", self.app.quit)        
        self.trayIcon.setContextMenu(self.menu)
        
        self.trayIcon.show()
        self.trayIcon.activated.connect(self.clickHandler)
        
        # Timer to check for updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkForUpdates)
        self.timer.start(update_check_interval_minutes*60*1000)
        
        # Timer to update tooltip every minute
        self.tooltip_timer = QtCore.QTimer()
        self.tooltip_timer.timeout.connect(self.setTooltip)
        self.tooltip_timer.start(60*1000)
        
        # Initial check for updates
        self.checkForUpdates()
        
        sys.exit(self.app.exec_())
        
    def checkForUpdates(self):
        self.tooltip_timer.stop()
        self.system_updates = getSystemUpdates()
        self.aur_updates = getAURUpdates()
        self.lastChecked = 0
        self.displayUpdates()
        self.setTooltip()
        self.tooltip_timer.start(60*1000)
        
        
    def setTooltip(self):
        tooltip = "Last checked " + str(self.lastChecked) + " minutes ago."
        self.trayIcon.setToolTip(tooltip)
        self.lastChecked += 1
        
    def updatesAvailable(self):
        return len(self.system_updates) or len(self.aur_updates)
        
    def displayUpdates(self):
        body = ""
        title = ""
        if self.updatesAvailable():
            title = "Updates available!"
            body += "System Updates:\n" + formatData(self.system_updates)
            body += "\n\n"
            body += "AUR Updates:\n" + formatData(self.aur_updates)
        else:
            title = "System up to date."
            body += "No updates available."
        self.trayIcon.showMessage(title, body)
        
    def clickHandler(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.displayUpdates()
  

def main():
    updater = SystemTrayUpdateNotifier()

if __name__ == '__main__':
    main()
