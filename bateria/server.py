import sys, requests, select
from socket import *

base_url = 'http://localhost:4993{}'


serverPort = 12050 + int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))

serverSocket.listen(1)
#serverSocket.setblocking(0)

client_socket, client_address = serverSocket.accept()
client_socket.setblocking(0)
print('Connection established')

set1_position = (10.0, 10.0)

def distance(a, b):
    deltax = (a[0] -b[0]) ** 2
    deltay = (a[1] - b[1]) ** 2
    return (deltax + deltay) ** 0.5

def handle_battery():
        battery = requests.post(base_url.format('/getBattery'), json=sys.argv[1])
        battery = battery.text
        battery = battery.encode()
        battery = float(battery.replace('"', ''))

        position = requests.post(base_url.format('/getPosition'), json=sys.argv[1])
        position = position.text.split(',')[0:2]
        dist = distance( set1_position, (float(position[0][1:]), float(position[1])) )
        #if dist > float(battery) - 40:
        if float(battery) < 40:
            print("low battery! returning...")
            response = requests.post(base_url.format('/setDestiny'),
            json={'drone': sys.argv[1], 'position': (10,10)})
            return "low"
        return "high"

first_time_low_battery = False

while True:

    message = 'continue'
    readable, _, _ = select.select([client_socket], [], [], 0.5)
    if readable:
        #print("olaa")
        message = client_socket.recv(2048)
        message = message.decode()
    else:
        if not first_time_low_battery:
            battery = handle_battery()
            if battery == "low" and not first_time_low_battery:
                response = "im out " + sys.argv[1]
                client_socket.send(response.encode())
                first_time_low_battery = True

    #print('Received from ', client_address[0], ': ', message)
    if message == 'bateria':
        response = requests.post(base_url.format('/getBattery'), json=sys.argv[1])
        response = response.text

    elif message == 'chamada':
        response = 'presente' + sys.argv[1]
    elif message == 'posicao':
        response = requests.post(base_url.format('/getPosition'), json=sys.argv[1])
        response = response.text
    elif message == 'set1':
        response = requests.post(base_url.format('/setDestiny'), json={'drone': sys.argv[1], 'position': (10,10)})
        response = 'ok'
    elif message == 'set2':
        response = requests.post(base_url.format('/setDestiny'), json={'drone': sys.argv[1], 'position': (180,150)})
        response = 'ok'
    elif message == 'set3':
        response = requests.post(base_url.format('/setDestiny'), json={'drone': sys.argv[1], 'position': (190,50)})
        response = 'ok' 
    elif message == 'vote':
        response = input('-> ')
    elif message == 'continue':
        continue
    else:
        print('Comando nao identificado' + message)
        break

    client_socket.send(response.encode())
    
client_socket.close()
	 
