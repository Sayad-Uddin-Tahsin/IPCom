import customtkinter as ctk
from socket import *
import threading
from tkinter import messagebox
import time
import json
from urllib.request import urlopen
import os


ipcomServer_icon = "./Assets/IPCom.ico"
about_icon = "./Assets/Info.ico"
with open("data.json", "r") as f:
    data = json.load(f)
    current_version = data["version"]
    server_appearence_mode = data["server_appearence_mode"]
    server_color_theme = data["server_color_theme"]
    ipcom_appearence_mode = data["ipcom_appearence_mode"]
    ipcom_color_theme = data["ipcom_color_theme"]
    username = data['username']

ctk.set_appearance_mode(server_appearence_mode)
ctk.set_default_color_theme(server_color_theme)

def checkIfThemeUpdate():
    global server_appearence_mode

    while True:
        with open("data.json", "r") as f:
            appearence_mode = json.load(f)['server_appearence_mode']
        if appearence_mode != server_appearence_mode:
            server_appearence_mode = appearence_mode
            ctk.set_appearance_mode(appearence_mode)
        
        time.sleep(60)

threading.Thread(target=checkIfThemeUpdate, daemon=True).start()

root = ctk.CTk()
root.title("IPCom Server")

positionRight = int(root.winfo_screenwidth()/2 - 600/2)
positionDown = int(root.winfo_screenheight()/2 - 100/2)
root.geometry(f"600x100+{positionRight}+{positionDown-50}")
root.wm_iconbitmap(ipcomServer_icon)
root.resizable(0, 0)

clients = []
pending = []
threads = []
hostSocket = None

def edit_data(key, value):
    with open("data.json", 'r') as f:
        data = json.load(f)
    data[key] = value
    with open("data.json", 'w') as f:
        json.dump(data, f, indent=4)

def about():
    about = ctk.CTk()
    about.title("About")
    about.wm_iconbitmap(about_icon)
    about.geometry("360x120")
    about.resizable(0, 0)

    lbl1 = ctk.CTkLabel(about, text="About", font=('Comic Sans MS', 30, "bold"))
    year = time.strftime("%Y")
    if "2023" < year:
        lbl2 = ctk.CTkLabel(about, text=f"IPCom Server v{current_version} is running on your Computer\n\n© 2023 - " + year + " Tahsin Inc. All Rights Reserved",
                     justify=ctk.LEFT, font=('Segoe UI', 15))
    else:
        lbl2 = ctk.CTkLabel(about, text=f"IPCom Server v{current_version} is running on your Computer\n\n© 2023 Tahsin Inc. All Rights Reserved", justify=ctk.LEFT,
                     font=('Segoe UI', 15))

    lbl1.place(x=10)
    lbl2.place(x=10, y=40)

    about.mainloop()

def handle_clients(object, add: bool=False, remove: bool=False):
    if add:
        clients.append(object)
    elif remove:
        clients.remove(object)

def handle_pending(object, add: bool=False, remove: bool=False):
    if add:
        pending.append(object)
    elif remove:
        pending.remove(object)

class ListernerThread(threading.Thread):
    def __init__(self, pending):
        super().__init__()
        self.pending = pending
        self.terminate_flag = threading.Event()

    def run(self):
        while True:
            try:
                clientSocket, clientAddress = hostSocket.accept()
            except OSError as e:
                if str(e) == "[WinError 10038] An operation was attempted on something that is not a socket":
                    break 
                else:
                    raise e

            clientSocket.send(("SYSTEM||||||!!||||||{{{USERNAME}}}").encode("utf-8"))
            handle_pending(clientSocket, add=True)
            thread = ClientThread(clientSocket, clientAddress, pending, clients)
            threads.append(thread)
            thread.start()
            if self.terminate_flag.is_set():
                break

    def terminate(self):
        self.terminate_flag.set()

class MessageLogFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def add_system_msg(self, message):
        f = ctk.CTkFrame(self, border_width=3, corner_radius=15)
        label = ctk.CTkLabel(f, text=message, wraplength=400, justify="center", font=("Sogue UI", 11, "bold"), width=520, corner_radius=100)
        label.pack(anchor="w", fill=ctk.BOTH, pady=4, padx=12)
        f.pack(anchor="w", side="top", padx=10, pady=2)
        self.after(10, self._parent_canvas.yview_moveto, 1.0)
    
    def add_join_msg(self, sender, message):
        f = ctk.CTkFrame(self, border_width=3, corner_radius=15, border_color=("#90ee90", "#154734"))
        m = ctk.CTkLabel(f, text=f"{sender}: {message}", wraplength=400, justify="left", font=("Sogue UI", 11, "bold"), corner_radius=50)
        m.pack(anchor="w", padx=10, pady=6)
        f.pack(anchor="w", side="top", padx=10, pady=2)
        self.after(10, self._parent_canvas.yview_moveto, 1.0)
    
    def add_left_msg(self, sender, message):
        f = ctk.CTkFrame(self, border_width=3, border_color=("#FF0000", "#8B0000"), corner_radius=15)
        m = ctk.CTkLabel(f, text=f"{sender}: {message}", wraplength=400, justify="left", font=("Sogue UI", 12, "bold"), corner_radius=50)
        m.pack(anchor="w", padx=10, pady=6)
        f.pack(anchor="w", side="top", padx=10, pady=2)
        self.after(10, self._parent_canvas.yview_moveto, 1.0)

    
    def add_msg(self, sender, message):
        f = ctk.CTkFrame(self, border_width=2, border_color=("#a6a6a6", "#808080"), fg_color=("#a6a6a6", "#808080"), corner_radius=20)
        m = ctk.CTkLabel(f, text=f"{sender}: {message}", wraplength=400, justify="left", font=("Sogue UI", 12, "bold"), fg_color="transparent", bg_color="transparent", corner_radius=50)
        m.pack(anchor="w", padx=10, pady=6)
        f.pack(anchor="w", side="top", padx=10, pady=2)
        self.after(10, self._parent_canvas.yview_moveto, 1.0)

def startSocket():
    global clients, pending, hostSocket, isRunThread

    for widget in logFrame.winfo_children():
        widget.destroy()
    
    def copy(ip, port):
        text = f"Join me on my IPCom server at \"{ip}:{port}\" and let's chat together! Download IPCom now from https://github.com/Sayad-Uddin-Tahsin/IPCom/releases/."
        root.clipboard_append(text)
    
    positionRight = int(root.winfo_screenwidth()/2 - 600/2)
    positionDown = int(root.winfo_screenheight()/2 - 520/2)
    root.geometry(f"600x520+{positionRight}+{positionDown-50}")

    clients = []
    pending = []
    hostSocket = socket(AF_INET, SOCK_STREAM)
    hostSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)

    hostIp = gethostbyname(gethostname())
    portNumber = 0
    hostSocket.bind((hostIp, portNumber))
    hostSocket.listen()
    
    logFrame.add_system_msg(message="Server started on this moment")
    serverControlSwitch.configure(text="Server ON")
    saveConversationButton.pack(anchor="se", side="right", padx=13, pady=5, fill=None, expand=None)
    ip_text.configure(text=f"Server running at {hostSocket.getsockname()[0]}:{hostSocket.getsockname()[1]}", cursor="hand2")
    ip_text.bind("<Button-1>", lambda e: copy(hostSocket.getsockname()[0], hostSocket.getsockname()[1]))
    thread = ListernerThread(pending)
    thread.daemon = True
    threads.insert(0, thread)
    thread.start()

def stopSocket():

    def disconnect_and_close(isWarn: bool = False):
        global hostSocket, threads, clients, pending

        for pending_client in pending:
            pending_client.close()
        for client in clients:
            client.close()
        for i in threads:
            i.terminate()
        threads = []
        hostSocket.close()
        hostSocket = None

        clients = []
        pending = []

        positionRight = int(root.winfo_screenwidth()/2 - 600/2)
        positionDown = int(root.winfo_screenheight()/2 - 100/2)
        ip_text.configure(text="Server is not started yet.", cursor="arrow")
        ip_text.unbind("<Button-1>")
        root.geometry(f"600x100+{positionRight}+{positionDown-50}")
        serverControlSwitch.configure(text="Server OFF")
        saveConversationButton.pack_forget()
    
    if len(clients) != 0:
        if messagebox.YESNO("Hold on!!!", f"{len(clients)} Users are currently active on this server!\nDo you want to close the server?"):
            disconnect_and_close()
        else:
            pass
    else:
        disconnect_and_close()
    

def settingsWindow():
    def initiate_appearence_mode(mode: str, ipcom: bool=False):
        if mode == "system":
            if ipcom:
                edit_data("ipcom_appearence_mode", "system")
            else:
                edit_data("server_appearence_mode", "system")
        if mode == "light":
            if ipcom:
                edit_data("ipcom_appearence_mode", "light")
            else:
                edit_data("server_appearence_mode", "light")
        if mode == "dark":
            if ipcom:
                edit_data("ipcom_appearence_mode", "dark")
            else:
                edit_data("server_appearence_mode", "dark")
        if not ipcom:
            ctk.set_appearance_mode(mode)
    
    def initiate_color_theme(color: str, ipcom: bool=False):
        if color == "blue":
            if ipcom:
                edit_data("ipcom_color_theme", "blue")
            else:
                edit_data("server_color_theme", "blue")
        if color == "dark-blue":
            if ipcom:
                edit_data("ipcom_color_theme", "dark-blue")
            else:
                edit_data("server_color_theme", "dark-blue")
        if color == "green":
            if ipcom:
                edit_data("ipcom_color_theme", "green")
            else:
                edit_data("server_color_theme", "green")
        if not ipcom:
            ctk.set_default_color_theme(color)
        if ipcom:
            ctk.CTkLabel(ipcomFrame, text="* Restart may require for update", font=("Segoe UI", 11, "italic")).place(x=115, y=165)
        else:
            ctk.CTkLabel(serverFrame, text="* Restart may require for update", font=("Segoe UI", 11, "italic")).place(x=115, y=115)

    def save():
        name = str(ipcomUsernameEntry.get())
        if name == "Name for yourself" or len(name) == 0 or name == username:
            return
        if os.path.exists("data.json"):
            with open("data.json", 'r') as f:
                db = json.load(f)
        else:
            db = {}
        db['username'] = name
        with open("data.json", "w") as f:
            json.dump(db, f, indent=4)

    def validate_char_count(new_value):
        if len(new_value) > 20:
            return False
        return True
    
    win = ctk.CTk()
    win.title("IPCom Settings")

    positionRight = int(win.winfo_screenwidth()/2 - 590/2)
    positionDown = int(win.winfo_screenheight()/2 - 300/2)
    win.geometry(f"590x300+{positionRight-150}+{positionDown-100}")
    win.wm_iconbitmap(ipcomServer_icon)
    win.resizable(0, 0)

    aboutLabel = ctk.CTkLabel(win, text=f"IPCom v{current_version}", text_color=("#a6a6a6", "#808080"), font=("Consolas", 12, "underline"), justify="right")
    aboutLabel.pack(anchor="sw", padx=10, side="left")
    aboutLabel.bind("<Button-1>", lambda event: about())
    aboutLabel.bind("<Enter>", lambda event: aboutLabel.configure(cursor="hand2"))
    aboutLabel.bind("<Leave>", lambda event: aboutLabel.configure(cursor=""))

    settingsLabel = ctk.CTkLabel(win, text="IPCom Settings", font=("Comic Sans MS", 30, "bold"))
    settingsLabel.place(x=200)
    serverFrame = ctk.CTkFrame(win, width=280, height=150, fg_color="transparent", border_width=2)
    serverFrame.place(x=10, y=60)
    serverFrame.pack_propagate(0)
    serverFrameLabel = ctk.CTkLabel(win, text="IPCom Server", font=("Comic Sans MS", 14, "bold"), padx=4)
    serverFrameLabel.place(x=20, y=47)

    serverModeLabel = ctk.CTkLabel(serverFrame, text="Appearance Mode", font=("Comic Sans MS", 13, "bold"))
    serverModeLabel.place(x=12, y=6)
    serverintVarMode = ctk.IntVar(value=["system", "light", "dark"].index(server_appearence_mode))
    serverRadiobuttonSystem = ctk.CTkRadioButton(master=serverFrame, text="System", variable=serverintVarMode, value=0, command=lambda: initiate_appearence_mode("system"))
    serverRadiobuttonSystem.place(x=12, y=36)
    serverRadiobuttonLight = ctk.CTkRadioButton(master=serverFrame, text="Light", variable=serverintVarMode, value=1, command=lambda: initiate_appearence_mode("light"))
    serverRadiobuttonLight.place(x=100, y=36)
    serverRadiobuttonDark = ctk.CTkRadioButton(master=serverFrame, text="Dark", variable=serverintVarMode, value=2, command=lambda: initiate_appearence_mode("dark"))
    serverRadiobuttonDark.place(x=170, y=36)
    
    serverColorLabel = ctk.CTkLabel(serverFrame, text="Color Theme", font=("Comic Sans MS", 13, "bold"))
    serverColorLabel.place(x=12, y=60)
    serverintVarColor = ctk.IntVar(value=["blue", "dark-blue", "green"].index(server_color_theme))
    serverRadiobuttonBlue = ctk.CTkRadioButton(master=serverFrame, text="Blue", variable=serverintVarColor, value=0, command=lambda: initiate_color_theme("blue"))
    serverRadiobuttonBlue.place(x=12, y=90)
    serverRadiobuttonDarkBlue = ctk.CTkRadioButton(master=serverFrame, text="Dark Blue", variable=serverintVarColor, value=1, command=lambda: initiate_color_theme("dark-blue"))
    serverRadiobuttonDarkBlue.place(x=75, y=90)
    serverRadiobuttonGreen = ctk.CTkRadioButton(master=serverFrame, text="Green", variable=serverintVarColor, value=2, command=lambda: initiate_color_theme("green"))
    serverRadiobuttonGreen.place(x=170, y=90)

    ipcomFrame = ctk.CTkFrame(win, width=280, height=215, fg_color="transparent", border_width=2)
    ipcomFrame.place(x=300, y=60)
    ipcomFrame.pack_propagate(0)
    ipcomFrameLabel = ctk.CTkLabel(win, text="IPCom", font=("Comic Sans MS", 14, "bold"), padx=4)
    ipcomFrameLabel.place(x=310, y=47)

    ipcomChangeUsernameLabel = ctk.CTkLabel(ipcomFrame, text="Change Username", font=("Comic Sans MS", 13, "bold"))
    ipcomChangeUsernameLabel.place(x=12, y=6)
    ipcomUsernameEntry = ctk.CTkEntry(ipcomFrame, width=180, height=12, fg_color="transparent", placeholder_text=username, font=("Consolas", 12), validate="key", validatecommand=(ipcomFrame.register(validate_char_count), '%P'))
    ipcomUsernameEntry.bind("<Return>", lambda e: save())
    ipcomUsernameEntry.place(x=12, y=33)
    ipcomUsernameSaveButton = ctk.CTkButton(ipcomFrame, width=30, height=20, text="Save", command=save)
    ipcomUsernameSaveButton.place(x=200, y=33)

    ipcomModeLabel = ctk.CTkLabel(ipcomFrame, text="Appearance Mode", font=("Comic Sans MS", 13, "bold"))
    ipcomModeLabel.place(x=12, y=55)
    ipcomintVarMode = ctk.IntVar(value=["system", "light", "dark"].index(ipcom_appearence_mode) + 1)
    ipcomRadiobuttonSystem = ctk.CTkRadioButton(master=ipcomFrame, text="System", variable=ipcomintVarMode, value=1, command=lambda: initiate_appearence_mode("system", True))
    ipcomRadiobuttonSystem.place(x=12, y=85)
    ipcomRadiobuttonLight = ctk.CTkRadioButton(master=ipcomFrame, text="Light", variable=ipcomintVarMode, value=2, command=lambda: initiate_appearence_mode("light", True))
    ipcomRadiobuttonLight.place(x=100, y=85)
    ipcomRadiobuttonDark = ctk.CTkRadioButton(master=ipcomFrame, text="Dark", variable=ipcomintVarMode, value=3, command=lambda: initiate_appearence_mode("dark", True))
    ipcomRadiobuttonDark.place(x=170, y=85)
    
    ipcomColorLabel = ctk.CTkLabel(ipcomFrame, text="Color Theme", font=("Comic Sans MS", 13, "bold"))
    ipcomColorLabel.place(x=12, y=109)
    ipcomintVarColor = ctk.IntVar(value=["blue", "dark-blue", "green"].index(ipcom_color_theme) + 1)
    ipcomRadiobuttonBlue = ctk.CTkRadioButton(master=ipcomFrame, text="Blue", variable=ipcomintVarColor, value=1, command=lambda: initiate_color_theme("blue", True))
    ipcomRadiobuttonBlue.place(x=12, y=139)
    ipcomRadiobuttonDarkBlue = ctk.CTkRadioButton(master=ipcomFrame, text="Dark Blue", variable=ipcomintVarColor, value=2, command=lambda: initiate_color_theme("dark-blue", True))
    ipcomRadiobuttonDarkBlue.place(x=75, y=139)
    ipcomRadiobuttonGreen = ctk.CTkRadioButton(master=ipcomFrame, text="Green", variable=ipcomintVarColor, value=3, command=lambda: initiate_color_theme("green", True))
    ipcomRadiobuttonGreen.place(x=170, y=139)
    ctk.CTkLabel(ipcomFrame, text="Appearance Mode change here takes up to 1 min if running.", font=("Segoe UI", 10, "italic")).pack(anchor="e", pady=3, padx=3, side="bottom")

    win.mainloop()

IPandPORT = ""
title = ctk.CTkLabel(root, text="IPCom Server", font=("Comic Sans MS", 30, "bold"))
title.pack()
IP = ""
PORT = ""
ip_text = ctk.CTkLabel(root, text="Server is not started yet.", font=("Segoe UI", 14, "bold"))
ip_text.pack(pady=0)

settingsButton = ctk.CTkButton(root, text="⚙", width=25, command=settingsWindow)
settingsButton.place(x=10, y=10)

mLog_text = ctk.CTkLabel(root, text="Messaging Log", font=("Segoe UI", 16, "bold"))
mLog_text.place(x=10, y=101)

def switch_event():
    if serverControlSwitch.get() == 0:
        stopSocket()
    if serverControlSwitch.get() == 1:
        startSocket()


aboutLabel = ctk.CTkLabel(root, text=f"IPCom v{current_version}", text_color=("#a6a6a6", "#808080"), font=("Consolas", 12, "underline"), justify="right")
aboutLabel.pack(anchor="sw", padx=10, side="left")
aboutLabel.bind("<Button-1>", lambda event: about())
aboutLabel.bind("<Enter>", lambda event: aboutLabel.configure(cursor="hand2"))
aboutLabel.bind("<Leave>", lambda event: aboutLabel.configure(cursor=""))

serverControlFrame = ctk.CTkFrame(root, width=140, height=65, border_width=3)
serverControlFrame.place(x=450, y=7)
serverControlFrame.pack_propagate(0)
serverControlLabel = ctk.CTkLabel(serverControlFrame, text="Server Control", font=("Sogue UI", 12, "bold"))
serverControlLabel.pack(pady=3)
serverControlSwitch = ctk.CTkSwitch(serverControlFrame, text="Server OFF", command=switch_event)
serverControlSwitch.pack(anchor="center")

def saveConversationEvent():
    saveConversationButtonPlacement = saveConversationButton.pack_info()
    saveConversationButton.pack_forget()
    progressbar = ctk.CTkProgressBar(master=root)
    progressbar.pack(anchor="se", side="right", padx=13, pady=13, fill=None, expand=None)
    messages = []
    for msgFrame in logFrame.winfo_children():
        messageLabel = msgFrame.winfo_children()
        messages.append(messageLabel[0].cget("text"))
    messages[0] = f"{messages[0]} on {hostSocket.getsockname()[0]}:{hostSocket.getsockname()[1]}"
    if not os.path.exists(os.path.expanduser(f"~\\Documents\\IPCom Chat Log")):
        os.makedirs(os.path.expanduser(f"~\\Documents\\IPCom Chat Log"))
    name = os.path.expanduser(f"~\\Documents\\IPCom Chat Log\\chatlog - {int(time.time())}.txt")
    total_messages = len(messages)
    
    with open(name, 'w') as f:
        for i, message in enumerate(messages):
            f.write(message + "\n")
            
            progress_value = (i + 1) / total_messages * 100
            progressbar.set(progress_value)
            progressbar.update_idletasks()
    
    saveConversationButton.configure(text=f"Saved {name}!", state="disabled")
    progressbar.pack_forget()
    saveConversationButton.pack_configure(**saveConversationButtonPlacement)
    root.after(5000, lambda: [saveConversationButton.configure(text="Save Chat Log", state="normal")])

logFrame = MessageLogFrame(root, height=340, width=555)
logFrame.place(x=10, y=130)
saveConversationButton = ctk.CTkButton(root, text="Save Chat Log", command=saveConversationEvent, height=25)
class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address, pending, clients):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.pending = pending
        self.clients = clients
        self.terminate_flag = threading.Event()

    def run(self):
        try:
            message1 = None
            while not self.terminate_flag.is_set():
                try:
                    message = self.client_socket.recv(4120).decode("utf-8")
                except ConnectionResetError:
                    try:
                        handle_clients(self.client_socket, remove=True)
                        return
                    except:
                        try:
                            handle_pending(self.client_socket, remove=True)
                            return
                        except Exception as e:
                            if self.client_socket not in self.pending and self.client_socket not in self.clients:
                                pass
                    for client in clients:
                        if client is not self.client_socket:
                            client.send((f"SYSTEM||||||!!||||||{str(message1).replace('TO SYSTEM===', '')} just left the chat!").encode("utf-8"))
                    logFrame.add_left_msg("SYSTEM", f"{str(message1).replace('TO SYSTEM===', '')} just left the chat!")
                    break
                except ConnectionAbortedError as e:
                    if str(e) == "[WinError 10053] An established connection was aborted by the software in your host machine":
                        pass
                except OSError as e:
                    if str(e) == "[WinError 10038] An operation was attempted on something that is not a socket":
                        pass
                if str(message).startswith("TO SYSTEM===") and self.client_socket in pending:
                    message1 = message
                    message = ""
                    for client in clients:
                        client.send((f"SYSTEM||||||!!||||||{str(message1).replace('TO SYSTEM===', '')} just joined the chat!").encode())
                    handle_pending(self.client_socket, remove=True)
                    handle_clients(self.client_socket, add=True)
                    logFrame.add_join_msg("SYSTEM", f"{str(message1).replace('TO SYSTEM===', '')} just joined the chat!")
                    continue
                if message != "":
                    for client in clients:
                        if client is not self.client_socket:
                            client.send((message).encode("utf-8"))
                    sender, message = str(message).split("||||||!!||||||", 1)
                    logFrame.add_msg(sender, message)
        finally:
            self.client_socket.close()
            for client in clients:
                if client is not self.client_socket:
                    client.send((f"SYSTEM||||||!!||||||{str(message1).replace('TO SYSTEM===', '')} just left the chat!").encode("utf-8"))

            logFrame.add_left_msg("SYSTEM", f"{str(message1).replace('TO SYSTEM===', '')} just left the chat!")

    def terminate(self):
        self.terminate_flag.set()        

root.mainloop()
