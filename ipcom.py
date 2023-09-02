import tkinter as tk
from tkinter import ttk
import socket
import threading
from tkinter import messagebox
import json
import time
import random
import os
from urllib.request import urlopen


about_icon = "./Assets/Info.ico"
ipcom_icon = "./Assets/IPCom.ico"
with open("data.json", "r") as f:
    current_version = json.load(f)["version"]

def startUpdateCacheCleaning():
    cached_files = [file for file in os.listdir("./")]
    for file in cached_files:
        if "_updateCache" in file:
            os.remove(file)
        elif file.split(".")[0].endswith("_"):
            os.remove(file.replace("_", "", -1))
            os.rename(file, file.replace("_", ""))

threading.Thread(target=startUpdateCacheCleaning, daemon=True).start()

def updateWin():
    def is_newer_version(new_version):
        current_parts = list(map(int, current_version.split('.')))
        new_parts = list(map(int, new_version.split('.')))
        
        max_length = max(len(current_parts), len(new_parts))
        
        current_parts.extend([0] * (max_length - len(current_parts)))
        new_parts.extend([0] * (max_length - len(new_parts)))
        
        for part1, part2 in zip(current_parts, new_parts):
            if part1 > part2:
                return False
            elif part1 < part2:
                return True
        
        return False

    def get_response(url):
        response = None
        try:
            response = urlopen(url)
            data = response.read().decode("utf-8")
            json_data = json.loads(data)
            json_data['status'] = "ok"
            return json_data
        except Exception as e:
            if response is not None:
                retry_after_header = response.getheader("Retry-After")
                if retry_after_header:
                    retry_after = int(retry_after_header)
                    return {"status": "error", "code": e.code, "msg": e.reason, "retry-after": retry_after}
                else:
                    return {"status": "error", "code": e.code, "msg": e.reason}
            else:
                return {"status": "error", "msg": str(e)}
       
    root = tk.Tk()
    root.title("IPCom: Check for Update")
    positionRight = int(root.winfo_screenwidth()/2 - 430/2)
    positionDown = int(root.winfo_screenheight()/2 - 138/2)
    root.geometry(f"430x138+{positionRight}+{positionDown - 50}")
    root.resizable(0, 0)
    root.pack_propagate(True)

    def startUpdator():
        download_button.place(x=500000, y=9999999)
        threading.Thread(target=os.popen, args=("start \"\" \"IPCom Updater.exe\"", ), daemon=True).start()
        root.destroy()
        root.quit()
    
    msgLabel = tk.Label(root, text="Check for Update", font=('Comic Sans MS', 20, "bold"))
    msgLabel.pack()

    current_version_label = tk.Label(root, text=f"Running Version: {current_version}", font=("Segoe UI", 10))
    current_version_label.pack(padx=10, pady=5, anchor="nw")

    status_label = tk.Label(root, text="Status:", font=("Segoe UI", 10))
    status_label.pack(padx=10, side="left", anchor="nw")

    status_entry = tk.Entry(root, state="readonly", font=("consolas", 10), width=37, readonlybackground="white")
    status_entry.pack(pady=3, side="left", anchor="nw")

    status_entry.config(state="normal")
    status_entry.insert(0, "Searching for Update...")
    status_entry.config(state="readonly")
    
    download_button = ttk.Button(root, text="Download Update")
    download_button.place(x=1000, y=1000)
    def check_for_update():
        url = "https://api.github.com/repos/Sayad-Uddin-Tahsin/IPCom/releases/latest"
        response_data = get_response(url)
        if response_data['status'] != "error":
            is_new = is_newer_version(response_data['tag_name'])

            if is_new:
                status_entry.config(state="normal")
                status_entry.delete(0, "end")
                status_entry.insert(0, "Update Available!")
                status_entry.config(state="readonly")
                downloads_list = []
                if len(response_data['assets']) == 1:
                    downloads_list.append({
                        "name": response_data["assets"][0]["name"],
                        "url": response_data["assets"][0]["browser_download_url"]
                    })
                else:
                    for asset in response_data['assets']:
                        if "installer" in str(asset["name"]).lower():
                            continue
                        downloads_list.append({
                            "name": asset["name"],
                            "url": asset["browser_download_url"]
                        })
                with open("updates.json", "r") as f:
                    Udb = json.load(f)
                
                Udb["status"] = "available"
                Udb['download'] = downloads_list
                Udb['version'] = response_data["tag_name"]

                with open("updates.json", 'w') as f:
                    json.dump(Udb, f, indent=4)
                
                download_button.config(command=startUpdator)
                download_button.place(x=320, y=110)
            else:
                status_entry.config(state="normal")
                status_entry.delete(0, "end")
                status_entry.insert(0, "You are up to date!")
                status_entry.config(state="readonly")
        else:
            with open("updates.json", 'r') as f:
                Udb = json.load(f)
            if Udb == {}:
                status_entry.config(state="normal")
                status_entry.delete(0, "end")
                status_entry.insert(0, "You are up to date!")
                status_entry.config(state="readonly")
            else:
                status_entry.config(state="normal")
                status_entry.delete(0, "end")
                status_entry.insert(0, "Cached Update Available!")
                status_entry.config(state="readonly")
                download_button.config(command=startUpdator)
                download_button.place(x=320, y=110)

    threading.Thread(target=check_for_update, daemon=True).start()
    root.update_idletasks()
    root.mainloop()

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
                lobj.config(text=f"{lobj.cget('text')}{c}")
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
        ip, port = str(entry.get()).split(":", 1)
        window.destroy()
        main(ip, int(port))

    def handle_port_entry_event(event):
        connect()

    def handle_focus_in(event):
        entry = event.widget
        if entry.get() == "192.168.0.105:6060":
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def handle_focus_out(event):
        entry = event.widget
        if entry.get() == "":
            entry.insert(0, "192.168.0.105:6060")
            entry.config(fg="gray")

    def validate_entry(text):
        if all(c.isdigit() or c in [":", "."] for c in text):
            if str(text).count(":") > 1:
                error.config(text="* : can't be twice as it defines Port", font=("Segoe UI", 8, 'italic'),
                            fg="red", justify="right")
                error.place(x=120, y=92)
                save_button.place(y=112)
                return False
            if text == "":
                error.config(text="")
                save_button.place(y=98)
                return True
            else:
                port = ""
                if ":" in text:
                    port = text.split(":")[1]
                    if port != "" and (int(port) < 0 or int(port) > 65535):
                        error.config(text="* Port must be within 0-65535", font=("Segoe UI", 8, 'italic'),
                                    fg="red", justify="right")
                        error.place(x=135, y=92)
                        save_button.place(y=112)
                        save_button.config(state=tk.DISABLED)
                        return False
                error.config(text="")
                save_button.place(y=98)
                if ":" in text and port != "":
                    save_button.config(state=tk.NORMAL)
                elif port == "":
                    save_button.config(state=tk.DISABLED)

                return True
        else:
            error.config(text="* IP & Port must be a number!\nEx. 192.168.0.105:6060", font=("Segoe UI", 8, 'italic'),
                        fg="red", justify="right")
            error.place(x=135, y=92)
            save_button.place(y=125)
            save_button.config(state=tk.DISABLED)
            return False


    window = tk.Tk()
    positionRight = int(window.winfo_screenwidth()/2 - 400/2)
    positionDown = int(window.winfo_screenheight()/2 - 155/2)
    window.geometry(f"400x155+{positionRight}+{positionDown-50}")
    window.title("Connect to a Server")
    window.wm_iconbitmap(ipcom_icon)
    window.resizable(0, 0)


    title = tk.Label(window, text="Connect to a Server", font=("Comic Sans MS", 20, "bold"))
    title.pack()
    enter_port_text = tk.Label(window, text="Enter the Port", font=("Segoe UI", 11, 'bold'))
    enter_port_text.pack()
    error = tk.Label(window, text="")
    error.place(x=5, y=45)

    placeholder = "192.168.0.105:6060"
    entry = tk.Entry(window, width=23, fg="gray", font=("Consolas", 10))
    entry.insert(0, placeholder)
    entry.bind("<FocusIn>", handle_focus_in)
    entry.bind("<FocusOut>", handle_focus_out)
    entry.bind("<Return>", handle_port_entry_event)
    entry.place(x=118, y=72)

    validate_cmd = window.register(validate_entry)
    entry.config(validate="key", validatecommand=(validate_cmd, "%P"))

    save_button = ttk.Button(window, text="Connect", style='W.TButton', command=connect, state=tk.DISABLED)
    save_button.place(x=208, y=98)

    window.mainloop()

def main(ip, port):
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
    othersMenu.add_command(label="Check for Update", command=updateWin)
    othersMenu.add_command(label="About", command=about)

    menu_bar.add_cascade(label="More", menu=othersMenu)

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

    title = tk.Label(root, text="IPCom", font=("Comic Sans MS", 20, "bold"))
    title.pack()
    ip_text = tk.Label(root, text=f"Connected to {ip}:{port}", font=("Segoe UI", 10, "bold"))
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
        messagebox.showerror(
            title='Connection Lost',
            message='The connection was lost from the Server!'
        )
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
