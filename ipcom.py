import socket
import threading
import tkinter as tk

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

hostIp = "127.0.0.1"
portNumber = 7500

clientSocket.connect((hostIp, portNumber))

window = tk.Tk()
window.title("Connected To: "+ hostIp+ ":"+str(portNumber))

txtMessages = tk.Text(window, width=50)
txtMessages.grid(row=0, column=0, padx=10, pady=10)

txtYourMessage = tk.Entry(window, width=50)
txtYourMessage.insert(0,"Your message")
txtYourMessage.grid(row=1, column=0, padx=10, pady=10)

def sendMessage():
    clientMessage = txtYourMessage.get()
    txtMessages.insert(tk.END, "\n" + "You: "+ clientMessage)
    clientSocket.send(clientMessage.encode("utf-8"))

btnSendMessage = tk.Button(window, text="Send", width=20, command=sendMessage)
btnSendMessage.grid(row=2, column=0, padx=10, pady=10)

def recvMessage():
    while True:
        serverMessage = clientSocket.recv(1024).decode("utf-8")
        print(serverMessage)
        txtMessages.insert(tk.END, "\n"+serverMessage)

recvThread = threading.Thread(target=recvMessage)
recvThread.daemon = True
recvThread.start()

window.mainloop()
