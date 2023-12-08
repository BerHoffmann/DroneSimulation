##from socket import *

import socket
import sys, requests, time, types, select

import ast,random

base_url = 'http://localhost:4993{}'


serverName = "127.0.0.1"
serverPorts = range(12052, 12055) #12000
sockets = []

option1 = 0
option2 = 0

data_out_index = []

def get_position(pos_x, pos_y):
    pos = [0,0,0]
    arrived = 0
    a = time.time()
    while arrived < len(serverPorts):
        for i, port in enumerate(serverPorts):
            if i in data_out_index:
                arrived = arrived + 1
                continue
            sockets[i].sendto('posicao'.encode(),(serverName,port))
            sockets[i].setblocking(1)
            response = sockets[i].recv(1024)
            sockets[i].setblocking(0)
            if response.decode()[:6] == "im out":
                arrived = arrived + 1
                print('dei append de ',int(response.decode()[7:]) - 2 )
                data_out_index.append(int(response.decode()[7:]) - 2)
                continue  
            pos = response.decode()
            #print(pos)
            pos = ast.literal_eval(pos)
            if abs(pos_x - pos[0]) < 6 or abs(pos_y - pos[1]) < 6:
                arrived = arrived + 1
            if time.time() - a > 5:
                print('Received from ', port, ': ', response.decode())
                a = time.time()
        #time.sleep(5) 
        
        
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
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #para poder ter non blocking, onde coloquei mais abaixo
    clientSocket.setblocking(0)
    #time.sleep(0.1)
    try:
        clientSocket.connect((serverName, port))
    except socket.error as e:
        if e.errno == socket.errno.EINPROGRESS:
            while True:
                _, writable, _ = select.select([], [clientSocket], [], 0.1)
                if writable:
                    break  # Connection established or failed
        else:
            print("deu ruim")  

    sockets.append(clientSocket)
    poll = select.poll()
    poll.register(clientSocket)
    print('Connected to server on port {}'.format(port))


#consideracoes: o cara principal que vai decidir se determinado drone vai ou nao, a depender
#do nivel de bateria dele.
#se o drone verificar que ta com pouca bateria, este retorna. talvez sem avisar o drone central
#ideia: se o drone verificar que ta com pouca bateria, este manda uma msg pro central pra ele
#retirar este da lista de drones!

#proxima ideia: drone avisar que ta com pouca carga e voltar pra casa,
#alem de avisar master p ele tirar tal drone de sua lista!

def distance(a, b):
    deltax = (a[0] -b[0]) ** 2
    deltay = (a[1] - b[1]) ** 2
    return (deltax + deltay) ** 0.5

try:
    elected = False
    while True:
        global option1, option2
        option1 = 0
        option2 = 0
        message = "continue"
        # non blocking mode, so i can receive even im on input part
        readable, _, _ = select.select(sockets, [], [], 0.5)
        if readable:
            #print("aqui")
            for sock in readable:
                data = sock.recv(1024)
                data = data.decode()
                print("aqui2s")
                if data[:6] == "im out":
                    print('dei append aqui de ', int(data[7:]) - 2 )
                    data_out_index.append(int(data[7:]) - 2)
        else:
            if not elected:
                message = input('-> ')

        elected = False
        if message == 'bateria':
            for i, port in enumerate(serverPorts):
                if i in data_out_index:
                    continue
                sockets[i].sendto(message.encode(),(serverName,port))
                sockets[i].setblocking(1)
                response = sockets[i].recv(1024)
                sockets[i].setblocking(0)
                print('Received from ', port, ': ', response.decode()) 

        elif message == 'chamada':
            for i, port in enumerate(serverPorts):
                if i in data_out_index:
                    continue
                sockets[i].sendto(message.encode(),(serverName,port))
                sockets[i].setblocking(1)
                response = sockets[i].recv(1024)
                sockets[i].setblocking(0)
                print('Received from ', port, ': ', response.decode())
                if response.decode()[:6] == "im out":
                    data_out_index.append(int(response.decode()[7:]) - 2)
        elif message == 'set1':
            willIget = False
            for i, port in enumerate(serverPorts):
                a = random.uniform(-3,3)
                if i in data_out_index:
                    continue
                sockets[i].sendto("bateria".encode(),(serverName,port))
                sockets[i].setblocking(1)
                battery = sockets[i].recv(1024)
                sockets[i].setblocking(0)
                response = requests.post(base_url.format('/getPosition'), json="1")
                coord = response.text.encode().split(',')[0:2]
                dist = distance((10.0, 10.0), ( float(coord[0][1:]), float(coord[1]) ) )
                if float(battery.decode()[1:-2])*3 > dist:
                    willIget = True
                    requests.post(base_url.format('/setDestiny'), json={'drone': 1, 'position': (10, 10)})
                    sockets[i].sendto(message.encode(),(serverName,port))
                    sockets[i].setblocking(1)
                    response = sockets[i].recv(1024)
                    sockets[i].setblocking(0)
            if willIget:
                get_position(10, 10)
        elif message == 'set2':
            willIget = False
            for i, port in enumerate(serverPorts):
                a = random.uniform(-3,3)
                if i in data_out_index:
                    continue
                sockets[i].sendto("bateria".encode(),(serverName,port))
                sockets[i].setblocking(1)
                battery = sockets[i].recv(1024)
                sockets[i].setblocking(0)
                response = requests.post(base_url.format('/getPosition'), json="1")
                coord = response.text.encode().split(',')[0:2]
                dist = distance((180.0, 150.0), ( float(coord[0][1:]), float(coord[1]) ) )
                if float(battery.decode()[1:-2])*4 > dist:
                    willIget = True
                    requests.post(base_url.format('/setDestiny'), json={'drone': 1, 'position': (180, 150)})
                    sockets[i].sendto(message.encode(),(serverName,port))
                    sockets[i].setblocking(1)
                    response = sockets[i].recv(1024)
                    sockets[i].setblocking(0)
            if willIget:
                get_position(180, 150)
        elif message == 'set3':
            willIget = False
            for i, port in enumerate(serverPorts):
                a = random.uniform(-3,3)
                if i in data_out_index:
                    continue
                sockets[i].sendto("bateria".encode(),(serverName,port))
                sockets[i].setblocking(1)
                battery = sockets[i].recv(1024)
                sockets[i].setblocking(0)
                response = requests.post(base_url.format('/getPosition'), json="1")
                coord = response.text.encode().split(',')[0:2]
                dist = distance((190.0, 50.0), ( float(coord[0][1:]), float(coord[1]) ) )
                if float(battery.decode()[1:-2])*3 > dist:
                    willIget = True
                    requests.post(base_url.format('/setDestiny'), json={'drone': 1, 'position': (190, 50)})
                    sockets[i].sendto(message.encode(),(serverName,port))
                    sockets[i].setblocking(1)
                    response = sockets[i].recv(1024)
                    sockets[i].setblocking(0)
            if willIget:
                get_position(190, 50)
        elif message == 'vote':
            vencedor = 0
            voto1 = input('-> ')
            election(0,0, int(voto1))
            for i, port in enumerate(serverPorts):
                sockets[i].sendto(message.encode(),(serverName,port))
                sockets[i].setblocking(1)
                response = sockets[i].recv(1024)
                sockets[i].setblocking(0)
                vencedor = election(i, port, int(response))
            print('The winner is point ', vencedor)
            message = 'set{}'.format(vencedor)
            elected = True

        elif message == 'continue':
            continue
        
        else:
            print('Comando nao identificado')
    
except KeyboardInterrupt:
    for socket in sockets:
        socket.close()
