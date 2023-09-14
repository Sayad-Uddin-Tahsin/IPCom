import customtkinter as ctk
import socket
import threading
from tkinter import messagebox
import json
import time
import os

about_icon = "./Assets/Info.ico"
ipcom_icon = "./Assets/IPCom.ico"
with open("data.json", "r") as f:
    data = json.load(f)
    current_version = data["version"]
    server_appearence_mode = data["server_appearence_mode"]
    server_color_theme = data["server_color_theme"]
    ipcom_appearence_mode = data["ipcom_appearence_mode"]
    ipcom_color_theme = data["ipcom_color_theme"]
    username = data['username']

ctk.set_appearance_mode(ipcom_appearence_mode)
ctk.set_default_color_theme(ipcom_color_theme)

def checkIfThemeUpdate():
    global ipcom_appearence_mode

    while True:
        with open("data.json", "r") as f:
            appearence_mode = json.load(f)['ipcom_appearence_mode']
        if appearence_mode != ipcom_appearence_mode:
            ipcom_appearence_mode = appearence_mode
            ctk.set_appearance_mode(appearence_mode)
        
        time.sleep(60)

threading.Thread(target=checkIfThemeUpdate, daemon=True).start()


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
    about.geometry("340x120")
    about.resizable(0, 0)

    lbl1 = ctk.CTkLabel(about, text="About", font=('Comic Sans MS', 30, "bold"))
    year = time.strftime("%Y")
    if "2023" < year:
        lbl2 = ctk.CTkLabel(about, text=f"IPCom v{current_version} is running on your Computer\n\n© 2023 - " + year + " Tahsin Inc. All Rights Reserved",
                     justify=ctk.LEFT, font=('Segoe UI', 15))
    else:
        lbl2 = ctk.CTkLabel(about, text=f"IPCom v{current_version} is running on your Computer\n\n© 2023 Tahsin Inc. All Rights Reserved", justify=ctk.LEFT,
                     font=('Segoe UI', 15))

    lbl1.place(x=10)
    lbl2.place(x=10, y=40)

    about.mainloop()

def set_username():
    if check_profiled():
        return take_ip()
    
    def save():
        name = str(entry.get())
        if name == "Name for yourself" or len(name) == 0:
            return
        if os.path.exists("data.json"):
            with open("data.json", 'r') as f:
                db = json.load(f)
        else:
            db = {}
        db['username'] = name
        with open("data.json", "w") as f:
            json.dump(db, f, indent=4)
        window.destroy()
        take_ip()

    def validate_char_count(new_value):
        if len(new_value) > 20:
            return False
        return True

    window = ctk.CTk()
    positionRight = int(window.winfo_screenwidth()/2 - 400/2)
    positionDown = int(window.winfo_screenheight()/2 - 150/2)
    window.geometry(f"400x150+{positionRight}+{positionDown-50}")
    window.title("Welcome to IPCom")
    window.wm_iconbitmap(ipcom_icon)
    window.resizable(0, 0)


    title = ctk.CTkLabel(window, text="", font=("Comic Sans MS", 30, "bold"))

    def typeWrite(lobj: ctk.CTkLabel, text: str):
        try:
            lobj.configure(text="")
            for c in text:
                lobj.configure(text=f"{lobj.cget('text')}{c}")
                time.sleep(0.15)
            return
        except ctk.TclError as e:
            if str(e) == "invalid command name \".!CTkLabel\"":
                return

    threading.Thread(target=typeWrite, args=(title, "Welcome to IPCom!", ), daemon=True).start()
    title.pack()
    enter_port_text = ctk.CTkLabel(window, text="Set your username", font=("Segoe UI", 15, 'bold'))
    enter_port_text.pack()
    error = ctk.CTkLabel(window, text="")
    error.place(x=5, y=45)

    placeholder = "Name for yourself"

    entry = ctk.CTkEntry(window, width=180, height=12, fg_color="transparent", placeholder_text=placeholder, font=("Consolas", 12), validate="key", validatecommand=(window.register(validate_char_count), '%P'))
    entry.bind("<Return>", lambda e: save())
    entry.place(x=110, y=72)

    once_change_warn = ctk.CTkLabel(window, text="Note: This can be changed later.", font=("Segoe UI", 11, 'italic'), text_color=("#0c07e8", "#1077e0"), fg_color="transparent")
    once_change_warn.place(x=118, y=92)
    save_button = ctk.CTkButton(window, text="Join IPCom", command=save)
    save_button.place(x=215, y=116)

    window.mainloop()


def check_profiled():
    if os.path.exists("./data.json"):
        with open("data.json", 'r') as f:
            d = json.load(f)
        if 'username' in d and d['username'] != "":
            return True
    return False

def take_ip():
    def connect():
        ip, port = str(entry.get()).split(":", 1)
        window.destroy()
        main(ip, int(port))

    def handle_port_entry_event(event):
        connect()

    def validate_entry(text):
        if all(c.isdigit() or c in [":", "."] for c in text):
            if str(text).count(":") > 1:
                error.configure(text="* : can't be twice as it defines Port", font=("Segoe UI", 11, 'italic'),
                            text_color="red", justify="right")
                error.place(x=124, y=91)
                save_button.place(y=116)
                return False
            if text == "":
                error.configure(text="")
                save_button.place(y=102)
                return True
            else:
                port = ""
                if ":" in text:
                    port = text.split(":")[1]
                    if port != "" and (int(port) < 0 or int(port) > 65535):
                        error.configure(text="* Port must be within 0-65535", font=("Segoe UI", 11, 'italic'),
                                    text_color="red", justify="right")
                        error.place(x=140, y=92)
                        save_button.place(y=116)
                        save_button.configure(state=ctk.DISABLED)
                        return False
                error.configure(text="")
                save_button.place(y=102)
                if ":" in text and port != "":
                    save_button.configure(state=ctk.NORMAL)
                elif port == "":
                    save_button.configure(state=ctk.DISABLED)

                return True
        else:
            error.configure(text="* IP & Port must be a number!\nEx. 192.168.0.105:6060", font=("Segoe UI", 11, 'italic'),
                        text_color="red", justify="right")
            error.place(x=140, y=92)
            save_button.place(y=125)
            save_button.configure(state=ctk.DISABLED)
            return False


    window = ctk.CTk()
    positionRight = int(window.winfo_screenwidth()/2 - 400/2)
    positionDown = int(window.winfo_screenheight()/2 - 160/2)
    window.geometry(f"400x160+{positionRight}+{positionDown-50}")
    window.title("Connect to a Server")
    window.wm_iconbitmap(ipcom_icon)
    window.resizable(0, 0)


    title = ctk.CTkLabel(window, text="Connect to a Server", font=("Comic Sans MS", 30, "bold"))
    title.pack()
    enter_port_text = ctk.CTkLabel(window, text="  Enter the Server Address", font=("Segoe UI", 16, 'bold'))
    enter_port_text.pack()
    error = ctk.CTkLabel(window, text="", text_color=("#FF0000", "#BF0000"))
    error.place(x=5, y=45)

    placeholder = "192.168.0.105:6060"
    entry = ctk.CTkEntry(window, width=170, height=13, font=("Consolas", 12), placeholder_text=placeholder)
    entry.bind("<Return>", handle_port_entry_event)
    entry.place(x=118, y=72)

    validate_cmd = window.register(validate_entry)
    entry.configure(validate="key", validatecommand=(validate_cmd, "%P"))

    save_button = ctk.CTkButton(window, text="Connect", command=connect, state=ctk.DISABLED)
    save_button.place(x=208, y=102)

    window.mainloop()

class ScrollableLabelButtonFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def add_system_msg(self, message):
        f = ctk.CTkFrame(self, border_width=2, corner_radius=15)
        label = ctk.CTkLabel(f, text=message, wraplength=400, justify="center", font=("Sogue UI", 11, "bold"), width=520, corner_radius=100)
        label.pack(anchor="w", fill=ctk.BOTH, pady=2, padx=12)
        f.pack(anchor="w", side="top", padx=10, pady=2)
        self.after(10, self._parent_canvas.yview_moveto, 1.0)
    
    def add_other_msg(self, sender, message):
        f = ctk.CTkFrame(self, border_width=2, border_color=("#a6a6a6", "#808080"), fg_color=("#a6a6a6", "#808080"), corner_radius=20)
        s = ctk.CTkLabel(f, text=f"{sender}", wraplength=400, justify="left", font=("Sogue UI", 12, "bold"), corner_radius=50)
        s.pack(anchor="w", padx=10, pady=6)
        m = ctk.CTkLabel(f, text=message, wraplength=400, justify="left", font=("Sogue UI", 12), corner_radius=50)
        m.pack(side="top", pady=2, padx=10)
        f.pack(anchor="w", side="top", padx=10, pady=2)
        self.after(10, self._parent_canvas.yview_moveto, 1.0)

    
    def add_my_msg(self, message):
        f = ctk.CTkFrame(self, border_width=2, border_color=("#32a852", "#3b8c50"), fg_color=("#32a852", "#3b8c50"), corner_radius=20)
        s = ctk.CTkLabel(f, text=f"You", wraplength=400, justify="right", font=("Sogue UI", 12, "bold"), fg_color="transparent", bg_color="transparent", corner_radius=50)
        s.pack(anchor="e", padx=10, pady=6)
        m = ctk.CTkLabel(f, text=message, wraplength=400, justify="right", font=("Sogue UI", 12), corner_radius=50, fg_color="transparent", bg_color="transparent")
        m.pack(side="top", pady=4, padx=9)
        f.pack(anchor="e", side="top", padx=10, pady=4)
        self.after(10, self._parent_canvas.yview_moveto, 1.0)

def main(ip, port):
    root = ctk.CTk()
    root.title("IPCom")
    positionRight = int(root.winfo_screenwidth()/2 - 600/2)
    positionDown = int(root.winfo_screenheight()/2 - 505/2)
    root.geometry(f"600x505+{positionRight}+{positionDown-50}")
    root.wm_iconbitmap(ipcom_icon)
    root.resizable(0, 0)

    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        clientSocket.connect((ip, port))
        messagebox.showinfo(
            title="Connection Established!",
            message=f"Connection established with {ip}:{port}!"
        )
    except:
        messagebox.showerror(
            title='Failed to Establish Connection',
            message='The IP and Port seems not online!'
        )
        root.destroy()
        take_ip()
        return

    with open("data.json", 'r') as f:
        db = json.load(f)

    clientSocket.send((f"TO SYSTEM==={db['username']} ({socket.gethostname()})").encode("utf-8"))

    title = ctk.CTkLabel(root, text="IPCom", font=("Comic Sans MS", 30, "bold"))
    title.pack()
    ip_text = ctk.CTkLabel(root, text=f"Connected to {ip}:{port}", font=("Segoe UI", 13, "bold"))
    ip_text.pack(pady=0)

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
        win.wm_iconbitmap(ipcom_icon)
        win.resizable(0, 0)

        aboutLabel = ctk.CTkLabel(win, text=f"IPCom v{current_version}", text_color=("#a6a6a6", "#808080"), font=("Consolas", 12, "underline"), justify="right")
        aboutLabel.pack(anchor="sw", padx=10, side="left")
        aboutLabel.bind("<Button-1>", lambda event: about())
        aboutLabel.bind("<Enter>", lambda event: aboutLabel.configure(cursor="hand2"))
        aboutLabel.bind("<Leave>", lambda event: aboutLabel.configure(cursor=""))

        settingsLabel = ctk.CTkLabel(win, text="IPCom Settings", font=("Comic Sans MS", 30, "bold"))
        settingsLabel.place(x=200)
        serverFrame = ctk.CTkFrame(win, width=280, height=165, fg_color="transparent", border_width=2)
        serverFrame.place(x=300, y=60)
        serverFrame.pack_propagate(0)
        serverFrameLabel = ctk.CTkLabel(win, text="IPCom Server", font=("Comic Sans MS", 14, "bold"), padx=4)
        serverFrameLabel.place(x=310, y=47)

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
        ctk.CTkLabel(serverFrame, text="Appearance Mode change here takes up to 1 min if running.", font=("Segoe UI", 10, "italic")).pack(anchor="e", pady=3, padx=3, side="bottom")


        ipcomFrame = ctk.CTkFrame(win, width=280, height=200, fg_color="transparent", border_width=2)
        ipcomFrame.place(x=10, y=60)
        ipcomFrame.pack_propagate(0)
        ipcomFrameLabel = ctk.CTkLabel(win, text="IPCom", font=("Comic Sans MS", 14, "bold"), padx=4)
        ipcomFrameLabel.place(x=20, y=47)

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

        win.mainloop()

    def send_message(entry):
        message = str(entry.get())
        message = message.strip()
        if message == "Type your message here...":
            message = ""
        if message == "":
            return
        clientSocket.send(f"{db['username']}||||||!!||||||{message}".encode("utf-8"))
        scrollable_label_button_frame.add_my_msg(message)
        messageCTkEntry.delete(0, ctk.END)
    
    def updateWordCount(event):
        count = len(messageCTkEntry.get())
        wordCountLabel.configure(text=f"{str(count).zfill(4)}/4100")

    def validate_input(new_value):
        if len(new_value) <= 4100:
            return True
        else:
            return False
    
    settingsButton = ctk.CTkButton(root, text="⚙", width=25, command=settingsWindow)
    settingsButton.place(x=10, y=10)
    aboutLabel = ctk.CTkLabel(root, text=f"IPCom v{current_version}", text_color=("#a6a6a6", "#808080"), font=("Consolas", 12, "underline"), justify="right")
    aboutLabel.pack(anchor="sw", padx=10, side="bottom")
    aboutLabel.bind("<Button-1>", lambda event: about())
    aboutLabel.bind("<Enter>", lambda event: aboutLabel.configure(cursor="hand2"))
    aboutLabel.bind("<Leave>", lambda event: aboutLabel.configure(cursor=""))
    wordCountLabel = ctk.CTkLabel(root, text="0000/4100", text_color=("#a6a6a6", "#808080"), font=("Segoe UI", 10), justify="right")
    wordCountLabel.place(x=497, y=472)
    messageCTkEntry = ctk.CTkEntry(root, width=530, height=25, placeholder_text="Type your message here...", validate="key", validatecommand=(root.register(validate_input), '%P'))
    messageCTkEntry.bind("<Return>", lambda e: send_message(messageCTkEntry))
    messageCTkEntry.bind("<KeyRelease>", updateWordCount)
    messageCTkEntry.place(x=12, y=455)
    sendCTkButton = ctk.CTkButton(root, text="Send", width=15, height=25, command=lambda: send_message(messageCTkEntry))
    sendCTkButton.place(x=550, y=455)

    def connectionlost():
        messagebox.showerror(
            title='Connection Lost',
            message='The connection was lost from the Server!'
        )
        take_ip()
        return

    def recvMessage():
        while True:
            try:
                serverMessage = clientSocket.recv(1024).decode("utf-8")
            except ConnectionResetError or ConnectionAbortedError:
                connectionlost()
                break
            
            sender, message = serverMessage.split("||||||!!||||||", 1)
            if sender == "SYSTEM":
                if message == f"{db['username']}({socket.gethostname()}) just joined!" or message == "{{{USERNAME}}}":
                    continue
                scrollable_label_button_frame.add_system_msg(message)
                continue
            scrollable_label_button_frame.add_other_msg(sender, message)

    scrollable_label_button_frame = ScrollableLabelButtonFrame(master=root, height=360, width=560)
    scrollable_label_button_frame.pack(pady=5)
    scrollable_label_button_frame.add_system_msg("You joined on this moment")

    recvThread = threading.Thread(target=recvMessage)
    recvThread.daemon = True
    recvThread.start()

    root.mainloop()

set_username()
