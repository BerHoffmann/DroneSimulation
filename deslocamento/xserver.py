import sys, requests
from socket import *

base_url = 'http://localhost:4993{}'


serverPort = 12040 + int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))

serverSocket.listen(1)

client_socket, client_address = serverSocket.accept()
print('Connection established')

while True:
    message = client_socket.recv(2048)
    message = message.decode()
    print('Received from ', client_address[0], ': ', message)
    
    if message == 'chamada':
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
    else:
        print('Comando nao identificado')
        break

    client_socket.send(response.encode())
    
client_socket.close()
    
    
    
	 
