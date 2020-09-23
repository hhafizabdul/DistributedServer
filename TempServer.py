from PyQt5 import QtCore, QtGui, QtWidgets
import socket  
import threading
import os                 # Import socket module
import time
import sys

s4 = socket.socket()           # Create a socket object
s5 = socket.socket()
s = []
servers = []
host = socket.gethostname()     # Get local machine name
permissions = {}

def get_servers():
    try:
        filename = 'servers.txt'
        file = open(filename, 'r')
        lines = file.readlines()
        for i,j in enumerate(lines):
            lines[i] = int (lines[i].replace('\n','',1))
        return lines
    except FileNotFoundError:
        return ['3000', '3001', '3002']

ports = get_servers()

for i in range(len(ports)):
    soc = socket.socket()
    s.append(soc) 


def connection(s, port):
    print ('Server listening....')
    s.bind((host, port))            # Bind to the port
    s.listen(5)                     # Now wait for client connection.

def connectorForS4(): # being used in /post_route
    global s4
    s4 = socket.socket()

def connectorForS5(): # being used in /getFile_route
    global s5
    s5 = socket.socket()


def handler(s, port):
    folders = os.listdir(os.path.join('.',''))
    if not 'Server{}Files'.format(port) in set(folders):
        os.system('mkdir Server{}Files'.format(port))
    
    connection(s, port)
    global permissions
    while permissions[port]:
        try:
            if not permissions[port]:
                return
            conn, addr = s.accept()
            if not permissions[port]:
                return
        except Exception:
            print('Server was manually removed')
            return
        print('Got connection from', addr)
    
        request = conn.recv(10)

        if request == b'/post':
            print('In /post handler')
            conn.send(b'Done_1')
            post_route(conn, port, False)

        elif request == b'/getFile':
            conn.send(b'Done_2')
            getFile_route(conn, port, False, part=False)
            
        
        elif request == b'/getList':
            print('In /getList handler')
            conn.send(b'Done_3')
            getFile_route(conn, port)

        elif request == b'/post_part':
            conn.send(b'Done_4')
            print('in /partRecv handler')
            post_route(conn, port)

        elif request == b'/get_part':
            conn.send(b'Done_5')
            print('in /request_part handler')
            getFile_route(conn, port, False)



def post_route(conn, port, part=True):
    data1 = conn.recv(100)
    print('The file to be recieved')
    
    filename = recieveFile(conn ,port, data1.decode())

    conn.send('Thank you for connecting'.encode())
    conn.close()

    if not part:
        splittedFiles = splitter(s, port, filename)
            
        for i,p in enumerate(ports):
            print(p)
            if p != port:
                s4.connect((host, p))
                getFile_route(s4, port , False, True, splittedFiles[i]) #because we need to send file
                temp = splittedFiles[i].split(o_sys)
                temp[1] = '"{}"'.format(temp[1])
                temp = o_sys.join(temp)
                os.system('del {}'.format(temp))
                connectorForS4()
    # return filename

def recieveFile(conn, port, temp, part=False):
    filename = temp.split('\n')[0]
    temp = temp.replace(f'{filename}\n','',1)
    data1 = temp.encode()

    # if len(filename) > 25:
    #     filename = filename[-25:]
    print(f'recieving {filename}')
    if part:
        path = os.path.join(f'Server{port}Files','toBeMerged')
    else:
        path = f'Server{port}Files' 
    with open(os.path.join(f'{path}',f'{filename}'), 'wb') as f:
        
        # f.write(data1)
        del data1
        while True:
            data = conn.recv(1024)
            if not data:
                break
            # write data to a file
            f.write(data)
            
    f.close()
    
    if not part:
        return filename
    pass

def getFile_route(conn, port , getList = True, splitted = False , splittedFileNames='', part=True):
    if not splitted:
        data =b''
        if not getList:    
            data = conn.recv(100)
            file = data.decode()
            file = file.replace('/','',1)
            if part:
                sendFile(conn, os.path.join(f'Server{port}Files',f'{file}'))
            else:
                try:
                    comFile = partGetter(port, file)
                    sendFile(conn,comFile)
                    print(comFile)
                    os.system(f'del "{comFile}"')
                except Exception:
                    print('Server is Down as all parts are not present')
        else: #for sending listof files at server
            dirList(f'Server{port}Files')
            sendFile(conn, 'reqList.txt')
        # else:                           # for sending requested file
    elif splitted:
        conn.send(b'/post_part')
        
        if conn.recv(30) == b'Done_4':
            temp = splittedFileNames.split(o_sys)
            conn.send(temp[1].encode())
            sendFile(conn, splittedFileNames)
    print('Done sending')
    conn.close()

def sendFile(conn, filename):
    # try:
    #     f = open(filename,'rb')
    # except FileNotFoundError:
    #     conn.send(b'FileNotFound')
    #     return

    f = open(filename, 'rb')

    l = f.read(1024)
    while (l):
        conn.send(l)
        l = f.read(1024)
    f.close()
    pass

def dirList(dir):
    files = os.listdir(dir)
    direct = os.path.join(f'{dir}','')
    for i,f in enumerate(files):
        files[i] = f'{f}\t|  {os.stat(direct+f).st_size} B'
    
    with open('reqList.txt', 'w') as l:
        l.write('\n'.join(files))
    pass


def splitter(s, port, filename):
    names = []
    p = []

    for i in range(len(ports)):
        names.append(os.path.join(f'Server{port}Files',f'{filename}_{i}_{len(ports)}'))
        
        filePart = open(names[i], 'wb')
        p.append(filePart)

    f = open(os.path.join(f'Server{port}Files',f'{filename}'),'rb')

    l = f.read(1024)
    
    while l:
        for i in range(len(ports)):
            p[i].write(l)
            l = f.read(1024)
    
    f.close()
    
    for i in range(len(ports)):
        p[i].close()
    filename = os.path.join(f'Server{port}Files',f'{filename}')
    temp = filename.split(o_sys)
    temp[1] = f'"{temp[1]}"'
    temp = o_sys.join(temp)

    os.system(f'del {temp}')
    return names
    # pass

def partGetter(port, filename):
    parts = {}
    name_check = 0
    for p in ports:
        if p != port:
            s5.connect((host,p))
            s5.send(b'/getList')
            fileList = ''
            if s5.recv(10) == b'Done_3' :
                while True:
                    data = s5.recv(1024)
                    if not data:
                        break
                    fileList = f'{fileList}{data.decode()}' 
                s5.close()
                fileList = fileList.split('\n')
                for i,f in enumerate(fileList):
                    
                    f = f.split('\t')[0]
                    fileList[i]=f
                    # print(f'f[:-4] = {f[:-4]} and filename = {filename}')
                    if f[:-4] == filename[:-4]:
                        parts[int(f[-3])] = [f, p]
                s5.close()
                connectorForS5()

            # return fileList
    # print(parts)
    # print(f'len of parts array = {len(parts)+1} and file showing parts is {parts[1][0][-1]}')
    # no_of_parts = 0
    try:
        if len(parts)+1 != int(parts[1][0][-1]):
            # no_of_parts = int(parts[1][0][-1])
            raise Exception
    except Exception:
        try:
            if len(parts)+1 != int(parts[0][0][-1]):
                raise Exception()
        except Exception:
            try:
                if len(parts)+1 != int(parts[2][0][-1]):
                    raise Exception
            except Exception:
                raise Exception

    os.system(f'mkdir {os.path.join(f"Server{port}Files","toBeMerged")}')

    part_paths = [os.path.join(f'Server{port}Files',f'{filename}')]

    print('recieving parts')

    for k in sorted(parts.keys()):
        # if p != port: 
        s5.connect((host,parts[k][1]))
        s5.send(b'/get_part')
        if s5.recv(10) == b'Done_5':
            s5.send(parts[k][0].encode())
            recieveFile(s5, port, parts[k][0], True)
            part_paths.append(os.path.join(f'Server{port}Files','toBeMerged',f'{parts[k][0]}'))
        connectorForS5()
    

    comFile = merger(part_paths)
    os.system(f'rmdir /s /q {os.path.join(f"Server{port}Files","toBeMerged")}')
    return comFile
            
    pass



def merger(fileParts):
    filename = fileParts[0][:-4]
    print(f'{fileParts} in meger')
    sortedParts = {}
    for temp in fileParts:
        print(temp)
        sortedParts[int(temp[-3])] = temp
    for k in sorted(sortedParts.keys()):
        fileParts[k] = sortedParts[k]

    part = []
    for i in range(len(fileParts)):
        p = open(fileParts[i],'rb')
        part.append(p)    

    f = open(filename, 'wb')
    r1 = part[0].read(1024)
    while r1:

        f.write(r1)
        check = fileParts[0].split(o_sys)[-1]
        for i in range(1,len(part),1):
            r2 = part[i].read(1024)
            f.write(r2)
            check = fileParts[i].split(o_sys)[-1]
        r1 = part[0].read(1024)
    return filename
    pass

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(328, 307)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.server = QtWidgets.QLineEdit(self.centralwidget)
        self.server.setGeometry(QtCore.QRect(40, 110, 113, 20))
        self.server.setObjectName("server")
        self.server.setPlaceholderText("Enter Server Port")
        
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(170, 50, 101, 151))
        self.listWidget.setObjectName("listWidget")
        global ports
        for i, p in enumerate(ports):
            self.listWidget.insertItem(i,str(p))
        self.listWidget.clicked.connect(self.listWidget_clicked)

        self.remove = QtWidgets.QPushButton(self.centralwidget)
        self.remove.setGeometry(QtCore.QRect(180, 210, 75, 23))
        self.remove.setObjectName("remove")
        self.remove.clicked.connect(self.removeServer)
        
        self.add = QtWidgets.QPushButton(self.centralwidget)
        self.add.setGeometry(QtCore.QRect(50, 140, 71, 23))
        self.add.setObjectName("add")
        self.add.clicked.connect(self.addServer)
        

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    global p_to_be_removed
    p_to_be_removed = 0
    def listWidget_clicked(self):
        temp = self.listWidget.currentItem()
        global p_to_be_removed
        p_to_be_removed = int(temp.text())
        pass

    def addServer(self):
        port = int(self.server.text())
        global ports
        global servers
        global s
        global permissions
        try:
            soc = socket.socket()
            t = threading.Thread(target=handler, args = (soc, port))
            permissions[port] = True
            t.daemon = True
            t.start()
            servers.append(t)
            s.append(soc)
            ports.append(port)
            self.listWidget.clear()
            for i, p in enumerate(ports):
               self.listWidget.insertItem(i,str(p))
        except Exception:
            print('Error while adding Server')
        pass

    def removeServer(self):
        global ports
        global servers
        global s
        global p_to_be_removed
        global permissions
        try:
            index = ports.index(p_to_be_removed)
            permissions[p_to_be_removed] = False
            ports.remove(p_to_be_removed)
            s[index].close()
            servers[index].join()
            servers.remove(servers[index])
            p_to_be_removed = 0
            s.remove(s[index])
            self.listWidget.clear()
            for i, p in enumerate(ports):
                self.listWidget.insertItem(i,str(p))
        except Exception:
            print('Error while removing server')
            pass    

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Server Controller"))
        self.remove.setText(_translate("MainWindow", "REMOVE"))
        self.add.setText(_translate("MainWindow", "ADD"))


if __name__ == '__main__':

    
    if len(sys.argv) == 1 :
        print('*****  python __file_name__ linux/windows gui(optional)  ****')
        sys.exit()
    # elif len(sys.argv) > 1 :
    #     if sys.argv[1] != 'windows' or sys.argv[1] != 'linux':
    #         sys.exit()
        
    for i in range(len(ports)):
        t = threading.Thread(target=handler, args=(s[i], ports[i]))
        # global permissions
        permissions[ports[i]] = True
        servers.append(t)

    for t in servers:
        t.daemon = True
        t.start()
    # time.sleep(0.5)

    global o_sys
    if sys.argv[1] == 'windows':
        o_sys = '\\'
    else:
        o_sys = '/'

    if len(sys.argv)>2:
        if sys.argv[2] == 'gui':
            app = QtWidgets.QApplication(sys.argv)
            MainWindow = QtWidgets.QMainWindow()
            ui = Ui_MainWindow()
            ui.setupUi(MainWindow)
            MainWindow.show()
            sys.exit(app.exec_())
    if input("Enter exit to Quit the program : ") == 'exit':
        sys.exit()
    else:
        while True:
            pass
    