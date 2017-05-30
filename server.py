import socket
import threading
import datetime
import time
import json


class ServerThread(threading.Thread):
    def __init__(self, cons_list, client, address, addr_list):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.cons_list = cons_list
        self.addr_list = addr_list

    def run(self):
        while True:
            raw_data = self.client.recv(4096)
            if not raw_data:
                # client is off-line, remove it and break the thread
                self.cons_list.remove(self.client)
                self.addr_list.remove(self.address)
                break

            # extract info from raw data
            data = json.loads(raw_data)
            text = data['msg']
            mode = data['private_mode']

            if mode in ['', 'None']:
                # public mode
                for client in self.cons_list:
                    client.send(self.msg_build(text, False))
            else:
                # private mode
                ip, port = str(mode).split(':')
                for i in range(len(self.cons_list)):
                    if self.cmpT(self.addr_list[i], (ip, int(port))):
                        # send msg to the specified ip and port
                        self.cons_list[i].send(self.msg_build(text, True))
                        break

    # construct the message
    def msg_build(self, text, private=False):
        send_time = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M')
        msg = ''
        if private:
            msg += '(Private Mode)'
        msg += 'From host: ' + self.address[0] + ', port: ' + str(
            self.address[1]) + ', time: ' + send_time + " \n      " + text
        return json.dumps({'msg': msg, 'cons': [x for x in self.addr_list]})

    # compare two list
    def cmpT(self, t1, t2):
        return sorted(t1) == sorted(t2)


class Server():
    def __init__(self):
        self.server = socket.socket()
        self.host = '127.0.0.1'
        self.port = 12345
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.cons_list = []
        self.addr_list = []
        self.thread = None

    def run(self):
        while True:
            try:
                con, addr = self.server.accept()
                print 'New Connection:', addr
                self.cons_list.append(con)
                self.addr_list.append(addr)
                self.thread = ServerThread(self.cons_list, con, addr, self.addr_list)
                self.thread.start()
            except Exception, e:
                print e
                break
        self.server.close()

s = Server()
s.run()
