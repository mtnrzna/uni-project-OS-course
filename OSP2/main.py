import random
from threading import Thread, Lock
import config
import math
from peer import Peer
number_of_all_peers = 10
number_of_all_rumors = 47

# create and append port numbers
for i in range(number_of_all_peers):
    config.ports.append(10000 +i)

#all_rumors = Rumors(number_of_all_peers, number_of_all_rumors)


#creating some rumors
rumor_template = '''RuMor rUmOR RumoR #'''
rumors = []
for i in range(number_of_all_rumors):
    rumors.append(rumor_template + str(i))

def get_ith_thread_rumors( peer_index):
    ith_thread_rumors = []
    #logic for calculating this peer's rumors from array of all rumors
    number_of_this_peers_rumor = 0
    if number_of_all_rumors % number_of_all_peers == 0:
        number_of_this_peers_rumor = number_of_all_rumors / number_of_all_peers
    else:
        if peer_index == number_of_all_peers -1: # if the current peer is the last peer
            other_peers_except_this_rumers = math.ceil(number_of_all_rumors / number_of_all_peers)
            number_of_this_peers_rumor = number_of_all_rumors - (other_peers_except_this_rumers * (number_of_all_peers -1))
        else: # if the current peer is anyone but the last one
            number_of_this_peers_rumor = math.ceil(number_of_all_rumors / number_of_all_peers)

    start_index = peer_index * math.ceil(number_of_all_rumors / number_of_all_peers)
    end_index = start_index + number_of_this_peers_rumor
    for i in range(start_index, end_index):
        ith_thread_rumors.append(rumors[i])
    #print(peer_index, ith_thread_rumors)
    return ith_thread_rumors

# creat random initial connected server to a peer
def get_connected_server_ports(peer_index):
    while True:
        i = random.randint(0, number_of_all_peers-1)
        if i != peer_index:
            break
    connected_servers_ports = []
    connected_servers_ports.append(str(config.ports[i]))
    #print(connected_servers)
    return connected_servers_ports


def get_ports_for_reqs_to_connect(peer_index):
    while True:
        i = random.randint(0, number_of_all_peers-1)
        if i != peer_index:
            break
    ports_for_reqs_to_connect = []
    ports_for_reqs_to_connect.append(str(config.ports[i]))
    #print(connected_servers)
    return ports_for_reqs_to_connect


def peer_thread(thread_index, write_to_file_lock):
    peer = Peer(thread_index, config.ports[thread_index], get_ith_thread_rumors(thread_index),get_connected_server_ports(thread_index), get_ports_for_reqs_to_connect(thread_index), write_to_file_lock)


with open("logs.txt", "w") as myfile:
    myfile.write("")

write_to_file_lock = Lock()
threads = []
for i in range(number_of_all_peers):
    t = Thread(target=peer_thread, args=(i,write_to_file_lock))
    threads.append(t)

for t in threads:
    t.start()


for t in threads:
    t.join()
