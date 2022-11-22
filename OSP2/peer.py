from threading import Thread, Lock
import socket
from color_prints import Colorprints
import time

class Peer(object):
    def __init__(self, peer_index, port, rumors, connected_servers_ports ,ports_for_reqs_to_connect, write_to_file_lock):
        self.peer_index = peer_index
        self.port = port
        self.rumors = rumors
        self.connected_servers_ports = connected_servers_ports
        self.ports_for_reqs_to_connect = ports_for_reqs_to_connect
        self.write_to_file_lock = write_to_file_lock

        self.print_initial_peer_status()

        self.rumors_lock = Lock()
        self.connected_server_ports_lock = Lock()

        self.run_server()

        def send2():
            self.send_rumors_to_all_connected_ports()
        def send1():
            self.send_ports_for_reqs_to_connect_to_all_connected_ports()   

        t1 = Thread(target=send1, args=())
        t1.start()
        t1.join()

        t2 = Thread(target=send2, args=())
        t2.start()
        t2.join()

        self.watch_rumors()


    def print_initial_peer_status(self):
        self.write_to_file_lock.acquire()
        txt = f"peer #{self.peer_index}, has initial rumors: {self.rumors}, initial connected ports:{self.connected_servers_ports}, peer to connect{self.ports_for_reqs_to_connect}"
        Colorprints.print_in_cyan(txt)
        with open("logs.txt", "a") as myfile:
            myfile.write(txt+ "\n")
        self.write_to_file_lock.release()




    def run_server(self):
        def server():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', self.port))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    while True:
                        raw_data = conn.recv(1024)
                        if raw_data:
                            data_list = raw_data.decode().split(",")
                            for data in data_list:
                                if data == "":
                                    break
                                command = data.split("|")[0].strip()
                                recieved_data = data.split("|")[1].strip()
                                for d in recieved_data:
                                    if d == "":
                                        recieved_data.remove(d)

                                if command == "rumor":
                                    if not recieved_data in self.rumors and len(recieved_data)>1:
                                        self.rumors_lock.acquire()
                                        self.rumors.append(recieved_data)
                                        self.rumors_lock.release()
                                        
                                        Colorprints.print_in_green(f"$$$peer #{self.peer_index} got new rumor!: {recieved_data}$$$")
                                        self.send_a_new_rumor_to_all_connected_ports(recieved_data)

                                elif command == "peer":
                                    if not recieved_data in self.connected_servers_ports and recieved_data != str(self.port):
                                        self.connected_server_ports_lock.acquire()
                                        self.connected_servers_ports.append(recieved_data)
                                        self.connected_server_ports_lock.release()
                                        Colorprints.print_in_yellow(f"***peer{self.peer_index} with port {self.port}'s connected to port {recieved_data}***")
                                        self.send_rumors_to_a_peer(recieved_data)


        t = Thread(target=server, args=())
        t.start()



    def send_a_new_rumor_to_all_connected_ports(self, rumor):
        def send():
            self.connected_server_ports_lock.acquire()
            connected_servers_ports = self.connected_servers_ports
            self.connected_server_ports_lock.release()
            for contd_serv_port in connected_servers_ports:
                self.send__a_new_rumor_to_a_peer(contd_serv_port, rumor)

        
        t = Thread(target=send, args=())
        t.start() 
        t.join() 


    def send__a_new_rumor_to_a_peer(self, port, rumor):
        #print(f"{self.port} {rumor}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', int(port)))
                Colorprints.print_in_purple(f"PORT {self.port} to PORT {port}: rumor {rumor}")
                s.sendall(bytes(f"rumor | {rumor},", encoding="utf-8"))
        #print("sending...")





    def send_rumors_to_all_connected_ports(self):
        def send():
            self.connected_server_ports_lock.acquire()
            connected_servers_ports = self.connected_servers_ports
            self.connected_server_ports_lock.release()
            for contd_serv_port in connected_servers_ports:
                self.send_rumors_to_a_peer(contd_serv_port)

        t = Thread(target=send, args=())
        t.start() 
        t.join() 


    def send_rumors_to_a_peer(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', int(port)))
                self.rumors_lock.acquire()
                for rumor in self.rumors:
                    Colorprints.print_in_purple(f"PORT {self.port} to PORT {port}: rumor {rumor}")
                    s.sendall(bytes(f"rumor | {rumor},", encoding="utf-8"))
                    #print("sending...")
                self.rumors_lock.release()





    def watch_rumors(self):
        def watch():  
            while True:

                self.rumors_lock.acquire()
                old_rumors = self.rumors
                self.rumors_lock.release()
                time.sleep(1)

                self.rumors_lock.acquire()
                new_rumors = self.rumors
                self.rumors_lock.release()

                if old_rumors == new_rumors:
                    self.write_to_file_lock.acquire()
                    txt = f"\npeer #{self.peer_index}, has rumors: {self.rumors}, connected ports:{self.connected_servers_ports}"
                    with open("logs.txt", "a") as myfile:
                        myfile.write(txt+ "\n")
                    self.write_to_file_lock.release()
                    break


                
        t = Thread(target=watch, args=())
        t.start() 





    def send_ports_for_reqs_to_connect_to_all_connected_ports(self):
        def send():
            self.connected_server_ports_lock.acquire()
            connected_servers_ports = self.connected_servers_ports
            self.connected_server_ports_lock.release()
            for contd_serv_port in connected_servers_ports:
                for port_to_cnct in self.ports_for_reqs_to_connect:
                    self.send_ports_for_reqs_to_a_peer(contd_serv_port, port_to_cnct)

        t = Thread(target=send, args=())
        t.start() 
        t.join() 



    def send_ports_for_reqs_to_a_peer(self, contd_serv_port, port_to_cnct):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', int(contd_serv_port)))
                Colorprints.print_in_lightPurple(f"PORT {self.port} to PORT {contd_serv_port}: peer 127.0.0.1 {port_to_cnct}")
                s.sendall(bytes(f"peer | {port_to_cnct},", encoding="utf-8"))
                #print("sending...")

