from socket import *
from threading import *

clients = set()
pending = set()

def clientThread(clientSocket, clientAddress):
    while True:
        try:
            message = clientSocket.recv(1024).decode("utf-8")
        except ConnectionResetError:
            try:
                clients.remove(clientSocket)
            except:
                pending.remove(clientSocket)
            print(clientAddress[0] + ":" + str(clientAddress[1]) +" disconnected")
            break
        if str(message).startswith("TO SYSTEM===") and clientSocket in pending:
            message1 = message
            message = ""
            for client in clients:
                print("sent")
                client.send((f"SYSTEM||||||!!||||||{str(message1).replace('TO SYSTEM===', '')} just joined!").encode())
            pending.remove(clientSocket)
            clients.add(clientSocket)
            print ("Connection established with: ", clientAddress[0] + ":" + str(clientAddress[1]))
            continue
        if message != "":
            for client in clients:
                if client is not clientSocket:
                    client.send((message).encode("utf-8"))
            
            sender, message = str(message).split("||||||!!||||||", 1)
            print(f"{sender}: {message}")
        
    clientSocket.close()

hostSocket = socket(AF_INET, SOCK_STREAM)
hostSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)

hostIp = "127.0.0.1"
portNumber = 5050
hostSocket.bind((hostIp, portNumber))
hostSocket.listen()
print(f"{hostSocket.getsockname()[0]}:{hostSocket.getsockname()[1]}")
print("Waiting for connection...")

while True:
    clientSocket, clientAddress = hostSocket.accept()
    clientSocket.send(("SYSTEM||||||!!||||||{{{USERNAME}}}").encode("utf-8"))
    pending.add(clientSocket)
    thread = Thread(target=clientThread, args=(clientSocket, clientAddress, ))
    thread.start()
