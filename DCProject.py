from PyQt5 import QtCore, QtGui, QtWidgets
from Clinet import Client

filename2 = []
files_selected = [] 
client = Client()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 340)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(70, 10, 125, 16))
        self.label.setObjectName("label")
        self.label.setFont(QtGui.QFont("Sanserif", 12))

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(210, 10, 111, 21))
        self.comboBox.setObjectName("server_ports")
        self.comboBox.clear
        self.comboBox.addItems(client.get_servers())
        # self.comboBox.view().pressed.connect(self.connectServer)

        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(70, 50, 270, 221))
        self.listWidget.setObjectName("server_files")
        self.listWidget.clicked.connect(self.listWidget_clicked)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(160, 290, 75, 23))
        self.pushButton.setObjectName("download")
        self.pushButton.clicked.connect(self.downloadFile)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(70, 290, 75, 23))
        self.pushButton_3.setObjectName("filesOnServer")
        self.pushButton_3.clicked.connect(self.ServerFiles)
        
        self.listWidget_2 = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_2.setGeometry(QtCore.QRect(380, 50, 270, 221))
        self.listWidget_2.setObjectName("directory_files_list")
        self.listWidget_2.clear()
        clientDirFiles = client.get_directory_files()

        for i, file in enumerate(clientDirFiles):
            self.listWidget_2.insertItem(i,file)
        self.listWidget_2.clicked.connect(self.listWidget_2_clicked)
        
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(480, 290, 75, 23))
        self.pushButton_2.setObjectName("upload")
        self.pushButton_2.clicked.connect(self.uploadFile)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
     
    def listWidget_2_clicked(self):
        item = self.listWidget_2.currentItem()
        global files_selected

        if item.background().color().getRgb() == (0, 0, 0, 255) or item.background().color().getRgb() == (0, 0, 0, 0):
            item.setBackground(QtGui.QColor(0, 150, 150, 255))    
            files_selected.append(item.text())
        else:
            item.setBackground(QtGui.QColor(0, 0, 0, 0))
            files_selected.remove(item.text())
        
        print(files_selected)

        pass

    def listWidget_clicked(self):
        item = self.listWidget.currentItem()
        global filename2 
        if item.background().color().getRgb() == (0, 0, 0, 255) or item.background().color().getRgb() == (0, 0, 0, 0):
            item.setBackground(QtGui.QColor(0, 150, 150, 255))    
            filename2.append(item.text())
        else:
            item.setBackground(QtGui.QColor(0, 0, 0, 0))
            filename2.remove(item.text())
        # filename2 = str(item.text())
        print(filename2)
        pass

    def uploadFile(self):
        port = int(self.comboBox.currentText())
        # global filename
        global files_selected
        # print(filename)
        for filename in files_selected:
            if filename in client.get_directory_files() and filename != "":
                print("uploading {}".format(filename))
                
                filename = filename.split('\t')[0]
                client.upload(port,filename)
            pass

    def downloadFile(self):
        port = int(self.comboBox.currentText())
        global filename2
        for filename in filename2:
            filename = filename.replace('\r','',1)
            filename = filename.split('\t')[0]
            client.download(port,filename)        
            self.clientFilesUpdate()    
        pass

    def ServerFiles(self):
        port = int(self.comboBox.currentText())
        serverFilesList = client.getServerFilesList(port)
        self.listWidget.clear()
        for i,file in enumerate(serverFilesList):
            self.listWidget.insertItem(i,file)
        pass

    def clientFilesUpdate(self):
        files = client.get_directory_files()
        self.listWidget_2.clear()
        for i, file in enumerate(files):
            self.listWidget_2.insertItem(i,file)
   
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DC Project"))
        self.pushButton.setText(_translate("MainWindow", "DOWNLOAD"))
        self.pushButton_2.setText(_translate("MainWindow", "UPLOAD"))
        self.label.setText(_translate("MainWindow", "Select Server Port"))
        self.pushButton_3.setText(_translate("MainWindow", "Server Files"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
