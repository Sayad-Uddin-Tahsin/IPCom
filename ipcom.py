import tkinter as tk
from tkinter import ttk
import socket
import threading
from tkinter.messagebox import showerror, showinfo
import json
import time
import random
import os

about_icon = "./Assets/Info.ico"
ipcom_icon = "./Assets/IPCom.ico"
current_version = "1.0"

def about():
    about = tk.Tk()
    about.title("About")
    about.wm_iconbitmap(about_icon)
    about.geometry("340x120")
    about.resizable(0, 0)

    lbl1 = tk.Label(about, text="About", font=('Comic Sans MS', 20, "bold"))
    year = time.strftime("%Y")
    if "2023" < year:
        lbl2 = tk.Label(about, text=f"IPCom v{current_version} is running on your Computer\n\n© 2023 - " + year + " Tahsin Inc. All Rights Reserved",
                     justify=tk.LEFT, font=('Segoe UI', 12))
    else:
        lbl2 = tk.Label(about, text=f"IPCom v{current_version} is running on your Computer\n\n© 2023 Tahsin Inc. All Rights Reserved", justify=tk.LEFT,
                     font=('Segoe UI', 12))

    lbl1.place(x=10)
    lbl2.place(x=10, y=40)

    about.mainloop()

def set_username():
    if check_profiled():
        return take_ip()
    
    def save():
        db = {}
        db['username'] = str(entry.get())
        with open("data.json", "w") as f:
            json.dump(db, f, indent=4)
        window.destroy()
        take_ip()

    def handle_focus_in(event):
        text = entry.get()

        if text == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def handle_focus_out(event):
        text = entry.get()

        if text.strip() == "":
            entry.insert(0, placeholder)
            entry.config(fg="gray")

    def validate_char_count(new_value):
        if len(new_value) > 20:
            return False
        return True

    window = tk.Tk()
    positionRight = int(window.winfo_screenwidth()/2 - 400/2)
    positionDown = int(window.winfo_screenheight()/2 - 150/2)
    window.geometry(f"400x150+{positionRight}+{positionDown-50}")
    window.title("Welcome to IPCom")
    window.wm_iconbitmap(ipcom_icon)
    window.resizable(0, 0)


    title = tk.Label(window, text="", font=("Comic Sans MS", 20, "bold"))

    def typeWrite(lobj: tk.Label, text: str):
        try:
            lobj.config(text="")
            for c in text:
                lobj.config(text=f"{str(lobj.cget('text')).replace('|', '')}{c}")
                time.sleep(0.15)
            return
        except tk.TclError as e:
            if str(e) == "invalid command name \".!label\"":
                return

    threading.Thread(target=typeWrite, args=(title, "Welcome to IPCom!", ), daemon=True).start()
    title.pack()
    enter_port_text = tk.Label(window, text="Set your username", font=("Segoe UI", 11, 'bold'))
    enter_port_text.pack()
    error = tk.Label(window, text="")
    error.place(x=5, y=45)

    placeholder = random.choice(['John', 'Andy', 'Joe', 'Johnson', 'Smith', 'Williams', 'Ashley', 'Jessica', 'Amanda', 'Brittany', 'Sarah', 'Samantha', 'Emily', 'Stephanie', 'Elizabeth', 'Megan'])

    entry = tk.Entry(window, width=25, fg="gray", font=("Consolas", 10), validate="key", validatecommand=(window.register(validate_char_count), '%P'))
    entry.insert(0, placeholder)
    entry.bind("<FocusIn>", handle_focus_in)
    entry.bind("<FocusOut>", handle_focus_out)
    entry.bind("<Return>", lambda e: save())
    entry.place(x=110, y=72)

    once_change_warn = tk.Label(text="Note: This cannot be changed later.", font=("Segoe UI", 8, 'italic'), fg="blue")
    once_change_warn.place(x=118, y=92)
    save_button = ttk.Button(window, text="Join IPCom", style='W.TButton', command=save)
    save_button.place(x=215, y=112)

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
        port = int(entry.get())
        window.destroy()
        main(port)

    def handle_port_entry_event(event):
        connect()

    def handle_focus_in(event):
        text = entry.get()

        if text == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def handle_focus_out(event):
        text = entry.get()

        if text.strip() == "":
            entry.insert(0, placeholder)
            entry.config(fg="gray")

    def validate_entry(text):
        if text.isdigit() or text == "":
            if text == "":
                error.config(text="")
                save_button.config(state=tk.NORMAL)
                save_button.place(y=98)
                return True
            else:
                error.config(text="")
                save_button.config(state=tk.NORMAL)
                save_button.place(x=190, y=98)
                return True
        elif not text.isdigit():
            error.config(text="* Port must be a number! Ex. 6060", font=("Segoe UI", 8, 'italic'),
                         fg="red")
            error.place(x=92, y=92)
            save_button.place(y=112)
            return False
        else:
            pass

    window = tk.Tk()
    positionRight = int(window.winfo_screenwidth()/2 - 400/2)
    positionDown = int(window.winfo_screenheight()/2 - 150/2)
    window.geometry(f"400x150+{positionRight}+{positionDown-50}")
    window.title("Connect to a Server")
    window.wm_iconbitmap(ipcom_icon)
    window.resizable(0, 0)


    title = tk.Label(window, text="Connect to a Server", font=("Comic Sans MS", 20, "bold"))
    title.pack()
    enter_port_text = tk.Label(window, text="Enter the Port", font=("Segoe UI", 11, 'bold'))
    enter_port_text.pack()
    error = tk.Label(window, text="")
    error.place(x=5, y=45)

    placeholder = "6060"

    ip_text = tk.Label(window, text="127.0.0.1:", font=("Consolas", 10))
    ip_text.place(x=135, y=70)
    entry = tk.Entry(window, width=7, fg="gray", font=("Consolas", 10))
    entry.insert(0, placeholder)
    entry.bind("<FocusIn>", handle_focus_in)
    entry.bind("<FocusOut>", handle_focus_out)
    entry.bind("<Return>", handle_port_entry_event)
    entry.place(x=212, y=72)

    validate_cmd = window.register(validate_entry)
    entry.config(validate="key", validatecommand=(validate_cmd, "%P"))

    save_button = ttk.Button(window, text="Connect", style='W.TButton', command=connect)
    save_button.place(x=190, y=98)

    window.mainloop()

def main(port):
    root = tk.Tk()
    root.title("IPCom")
    positionRight = int(root.winfo_screenwidth()/2 - 600/2)
    positionDown = int(root.winfo_screenheight()/2 - 500/2)
    root.geometry(f"600x500+{positionRight}+{positionDown-50}")
    root.wm_iconbitmap(ipcom_icon)
    root.resizable(0, 0)

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    othersMenu = tk.Menu(menu_bar, tearoff=0)
    othersMenu.add_command(label="About", command=about)
    menu_bar.add_cascade(label="More", menu=othersMenu)

    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        hostIp = "127.0.0.1"

        clientSocket.connect((hostIp, port))
        showinfo(
            title="Connection Established!",
            message=f"Connection established with {hostIp}:{port}!"
        )
    except:
        showerror(
            title='Failed to Establish Connection',
            message='The IP and Port seems not online!'
        )
        root.destroy()
        take_ip()
        return

    with open("data.json", 'r') as f:
        db = json.load(f)

    clientSocket.send((f"TO SYSTEM==={db['username']} ({socket.gethostname()})").encode("utf-8"))

    title = tk.Label(root, text="IPCom", font=("Comic Sans MS", 20, "bold"))
    title.pack()
    ip_text = tk.Label(root, text=f"Connected to: 127.0.0.1:{port}", font=("Segoe UI", 10, "bold"))
    ip_text.pack(pady=0)
    mFrame = tk.Frame(root, highlightbackground="black", highlightthickness=1, height=360, width=570)
    mFrame.place(x=12, y=75)
    mFrame.pack_propagate(False)

    canvas = tk.Canvas(mFrame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(mFrame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    def on_entry_click(event):
        if messageEntry.get() == "Type your message here...":
            messageEntry.delete(0, "end")
            messageEntry.config(fg="black")

    def on_entry_leave(event):
        if messageEntry.get() == "":
            messageEntry.insert(0, "Type your message here...")
            messageEntry.config(fg="gray")

    def send_message(entry):
        message = str(entry.get())
        message = message.strip()
        if message == "Type your message here...":
            message = ""
        if message == "":
            return
        clientSocket.send(f"{db['username']}||||||!!||||||{message}".encode("utf-8"))
        sFrame = tk.Frame(inner_frame, highlightbackground="black", highlightthickness=1)
        sFrame.pack(anchor="e", side="top", padx=10, pady=2)
        n = tk.Label(sFrame, text=f"You", wraplength=400, justify="left", font=("Sogue UI", 9, "bold"))
        n.pack(anchor="e")
        l = tk.Label(sFrame, text=message, wraplength=400, justify="left")
        l.pack()

        messageEntry.delete(0, tk.END)
        root.focus()
        messageEntry.insert(0, "Type your message here...")
        messageEntry.bind("<FocusIn>", on_entry_click)
        messageEntry.bind("<FocusOut>", on_entry_leave)

        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(1.0)


    messageEntry = tk.Entry(root, width=80)
    messageEntry.insert(0, "Type your message here...")
    messageEntry.bind("<FocusIn>", on_entry_click)
    messageEntry.bind("<FocusOut>", on_entry_leave)
    messageEntry.bind("<Return>", lambda e: send_message(messageEntry))
    messageEntry.place(x=12, y=450)
    sendButton = tk.Button(root, text="Send", height=1, width=10, command=lambda: send_message(messageEntry))
    sendButton.place(x=500, y=446)

    inner_frame = tk.Frame(canvas, )
    canvas.create_window((0, 0), window=inner_frame, anchor='nw')

    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_mousewheel(event):
        canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    inner_frame = tk.Frame(canvas, height=350, width=550)
    inner_frame.pack_propagate(True)
    canvas.create_window((0, 0), window=inner_frame, anchor='nw')

    def connectionlost():
        showerror(
            title='Connection Lost',
            message='The connection was lost from the Server!'
        )
        # root.quit()
        root.destroy()
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
                sFrame = tk.Frame(inner_frame, highlightbackground="black", highlightthickness=1)
                sFrame.pack(anchor="w", side="top", padx=10, pady=2)
                n = tk.Label(sFrame, text=message, wraplength=400, justify="center", font=("Sogue UI", 9, "bold"), width=74)
                n.pack(anchor="w", fill=tk.BOTH)
                continue
            sFrame = tk.Frame(inner_frame, highlightbackground="black", highlightthickness=1)
            sFrame.pack(anchor="w", side="top", padx=10, pady=2)
            n = tk.Label(sFrame, text=f"{sender}", wraplength=400, justify="left", font=("Sogue UI", 9, "bold"))
            n.pack(anchor="w")
            l = tk.Label(sFrame, text=message, wraplength=400, justify="left")
            l.pack()
            inner_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

    sFrame = tk.Frame(inner_frame, highlightbackground="black", highlightthickness=1)
    sFrame.pack(anchor="w", side="top", padx=10, pady=2)
    n = tk.Label(sFrame, text=f"You joined on this moment", wraplength=400, justify="center", font=("Sogue UI", 9, "bold"), width=74)
    n.pack(anchor="w", fill=tk.BOTH)

    recvThread = threading.Thread(target=recvMessage)
    recvThread.daemon = True
    recvThread.start()

    canvas.bind('<Configure>', update_scrollregion)
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    root.mainloop()

set_username()
