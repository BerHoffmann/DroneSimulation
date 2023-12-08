from socket import *

import sys, requests, time, types, select

import ast,random

base_url = 'http://localhost:4993{}'


serverName = "127.0.0.1"
serverPorts = range(12042, 12050)
sockets = []

option1 = 0
option2 = 0

def get_position(pos_x, pos_y):
    pos = [0,0,0]
    arrived = 0
    while arrived < len(serverPorts):
        for i, port in enumerate(serverPorts):
            sockets[i].sendto('posicao'.encode(),(serverName,port))
            response = sockets[i].recv(1024)
            pos = response.decode()
            pos = ast.literal_eval(pos)
            if abs(pos_x - pos[0]) < 6 or abs(pos_y - pos[1]) < 6:
                arrived = arrived + 1
            print('Received from ', port, ': ', response.decode())
        time.sleep(5) 
        
        
def election(i, port, response):
    global option1, option2
    if response == 1:
        option1 = option1 + 1
    elif response == 3:
        option2 = option2 + 1
    else:
        sockets[i].sendto(message.encode(),(serverName, port))
        response = sockets[i].recv(1024)
        vencedor = election(i, port, response)
       
    if option1 > option2: 
        return 1
    else:
        return 3
                    
                    
for i, port in enumerate(serverPorts):
    clientSocket = socket(AF_INET,SOCK_STREAM)
    clientSocket.connect((serverName, port))
    sockets.append(clientSocket)
    poll = select.poll()
    poll.register(clientSocket)
    print('Connected to server on port {}'.format(port))


try:
    elected = False
    while True:
        global option1, option2
        option1 = 0
        option2 = 0
        if not elected:
            message = input('-> ')
        elected = False
        if message == 'chamada':
            for i, port in enumerate(serverPorts):
                sockets[i].sendto(message.encode(),(serverName,port))
                response = sockets[i].recv(1024)
                print('Received from ', port, ': ', response.decode()) 
        elif message == 'set1':
            for i, port in enumerate(serverPorts):
                a = random.uniform(-3,3)
                requests.post(base_url.format('/setDestiny'), json={'drone': 1, 'position': (10,10)})
                sockets[i].sendto(message.encode(),(serverName,port))
                response = sockets[i].recv(1024)
            get_position(10, 10)
        elif message == 'set2':
            for i, port in enumerate(serverPorts):
                a = random.uniform(-3,3)
                requests.post(base_url.format('/setDestiny'), json={'drone': 1, 'position': (180, 150)})
                sockets[i].sendto(message.encode(),(serverName,port))
                response = sockets[i].recv(1024)
            get_position(180, 150)
        elif message == 'set3':
            for i, port in enumerate(serverPorts):
                a = random.uniform(-3,3)
                requests.post(base_url.format('/setDestiny'), json={'drone': 1, 'position': (190, 50)})
                sockets[i].sendto(message.encode(),(serverName,port))
                response = sockets[i].recv(1024)
            get_position(190, 50)
        elif message == 'vote':
            vencedor = 0
            voto1 = input('-> ')
            election(0,0, int(voto1))
            for i, port in enumerate(serverPorts):
                sockets[i].sendto(message.encode(),(serverName,port))
                response = sockets[i].recv(1024)
                vencedor = election(i, port, int(response))
            print('The winner is point ', vencedor)
            message = 'set{}'.format(vencedor)
            elected = True
                
        else:
            print('Comando nao identificado')
    
except KeyboardInterrupt:
    for socket in sockets:
        socket.close()
