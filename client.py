from PyQt4 import QtGui
import chat
from PyQt4.QtCore import *
from scapy.all import *
import socket
import json


class ClientThread(QThread):
    def __init__(self, client_window):
        QThread.__init__(self)
        self.client_window = client_window

    def run(self):
        while True:
            msg = self.client_window.socket.recv(4096)
            if not msg:
                break
            msg = json.loads(msg)
            cons = msg['cons']
            msg = msg['msg']
            self.emit(SIGNAL("output(PyQt_PyObject)"), msg)
            self.emit(SIGNAL("output1(PyQt_PyObject)"), cons)
            self.emit(SIGNAL("output2(PyQt_PyObject)"), cons)


class ClientWinow(QtGui.QMainWindow, chat.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.socket = None
        self.host = '127.0.0.1'
        self.msg_buffer = []
        self.thread = None
        self.ip.setText(self.host)
        self.port.setText('12345')
        self.quit_button.clicked.connect(self.quit)
        self.send_button.clicked.connect(self.send)
        self.start_button.clicked.connect(self.connect_server)
        self.terminal_button.clicked.connect(self.terminate)
        self.clear_button.clicked.connect(self.clear)
        self.running_status.setText("No Connection")

    def send(self):
        if self.thread is not None and self.thread.isRunning():
            text = str(self.input_window.toPlainText())
            private_mode = str(self.private_chat.currentText())
            self.socket.send(json.dumps({'private_mode': private_mode, 'msg': text}))
            self.input_window.clear()
        else:
            self.running_status.setText("No Connection")

    def private_con(self, cons):
        self.private_chat.clear()
        cons = [None] + cons
        for con in cons:
            if con is None:
                self.private_chat.addItem('None')
            else:
                self.private_chat.addItem(con[0] + ':' + str(con[1]))

    def print_msg(self, msg):
        self.chat_window.addItem(msg)

    def print_cons(self, cons):
        self.connection_list.clear()
        for con in cons:
            self.connection_list.addItem(con[0] + ': ' + str(con[1]))

    def connect_server(self):
        if self.thread is not None and self.thread.isRunning():
            self.running_status.setText("Already Connected, please stop the connection first")
        else:
            ip = str(self.ip.text())
            port = int(self.port.text())
            self.socket = socket.socket()
            self.socket.connect((ip, port))
            self.thread = ClientThread(self)
            self.connect(self.thread, SIGNAL("output(PyQt_PyObject)"), self.print_msg)
            self.connect(self.thread, SIGNAL("output1(PyQt_PyObject)"), self.print_cons)
            self.connect(self.thread, SIGNAL("output2(PyQt_PyObject)"), self.private_con)
            self.thread.start()
            self.running_status.setText("Connected")

    def terminate(self):
        if self.thread is not None and self.thread.isRunning():
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.clear()
            self.running_status.setText("No connection")

    def clear(self):
        self.chat_window.clear()
        self.input_window.clear()
        self.connection_list.clear()
        self.private_chat.clear()

    def quit(self):
        self.terminate()
        sys.exit(0)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    client = ClientWinow()
    client.show()
    app.exec_()
