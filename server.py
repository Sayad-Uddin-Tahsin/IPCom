import tkinter as tk
from tkinter import ttk
from socket import *
import threading
import winsound
import time
import json
from urllib.request import urlopen
import os


ipcomServer_icon = "./Assets/IPCom.ico"
about_icon = "./Assets/Info.ico"
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
root = tk.Tk()
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
    about.geometry("360x120")
    about.resizable(0, 0)

    lbl1 = tk.Label(about, text="About", font=('Comic Sans MS', 20, "bold"))
    year = time.strftime("%Y")
    if "2023" < year:
        lbl2 = tk.Label(about, text=f"IPCom Server v{current_version} is running on your Computer\n\n© 2023 - " + year + " Tahsin Inc. All Rights Reserved",
                     justify=tk.LEFT, font=('Segoe UI', 12))
    else:
        lbl2 = tk.Label(about, text=f"IPCom Server v{current_version} is running on your Computer\n\n© 2023 Tahsin Inc. All Rights Reserved", justify=tk.LEFT,
                     font=('Segoe UI', 12))

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

def startSocket():
    global clients, pending, hostSocket, isRunThread
    
    for widget in inner_frame.winfo_children():
        widget.destroy()

    def copy(ip, port):
        text = f"Join me on my IPCom server at \"{ip}:{port}\" and let's chat together! Download IPCom now from https://github.com/Sayad-Uddin-Tahsin/IPCom/releases/."
        root.clipboard_append(text)
    
    positionRight = int(root.winfo_screenwidth()/2 - 600/2)
    positionDown = int(root.winfo_screenheight()/2 - 385/2)
    root.geometry(f"600x385+{positionRight}+{positionDown-50}")
    connection_menu.entryconfig(0, state="disabled", activebackground="light grey")
    connection_menu.entryconfig(1, state="normal", activebackground="")

    clients = []
    pending = []
    hostSocket = socket(AF_INET, SOCK_STREAM)
    hostSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
    sFrame = tk.Frame(inner_frame, highlightbackground="black", highlightthickness=2)
    sFrame.pack(anchor="w", side="top", padx=10, pady=2)
    n = tk.Label(sFrame, text=f"Server started on this moment", wraplength=400, justify="center", font=("Sogue UI", 9, "bold"), width=74)
    n.pack(anchor="w", fill=tk.BOTH)

    hostIp = gethostbyname(gethostname())
    portNumber = 0
    hostSocket.bind((hostIp, portNumber))
    hostSocket.listen()

    ip_text.config(text=f"Server running at {hostSocket.getsockname()[0]}:{hostSocket.getsockname()[1]}", cursor="hand2")
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

        if isWarn:
            warningWin.destroy()

        clients = []
        pending = []
        
        connection_menu.entryconfig(0, state="normal", activebackground="")
        connection_menu.entryconfig(1, state="disabled", activebackground="light grey")
        positionRight = int(root.winfo_screenwidth()/2 - 600/2)
        positionDown = int(root.winfo_screenheight()/2 - 80/2)
        ip_text.config(text="Server is not started yet.", cursor="arrow")
        ip_text.unbind("<Button-1>")
        root.geometry(f"600x80+{positionRight}+{positionDown-50}")

    
    if len(clients) != 0:
        warningWin = tk.Tk()
        warningWin.title("Warning")
        positionRight = int(root.winfo_screenwidth()/2 - 600/2)
        positionDown = int(root.winfo_screenheight()/2 - 200/2)
        warningWin.geometry(f"400x120+{positionRight}+{positionDown-50}")
        warningWin.wm_iconbitmap(ipcomServer_icon)
        warningWin.resizable(0, 0)

        wLabel = tk.Label(warningWin, text="Hold on!!!", font=("Comic Sans MS", 20, "bold"))
        wLabel.pack()
        tLabel = tk.Label(warningWin, text=f"{len(clients)} Users are currently active on this server!\nDo you want to close the server?", font=("Sogue UI", 11, "bold"))
        tLabel.pack()
        
        closeBTN = tk.Button(warningWin, text="Cancel", command=warningWin.destroy, relief=tk.GROOVE)
        closeBTN.pack(anchor="se", side="right", padx=2)
        
        DcloseBTN = tk.Button(warningWin, text="Disconnect all and Close", command=lambda: disconnect_and_close(True), relief=tk.GROOVE)
        DcloseBTN.pack(anchor="se", side="right")
        thread1 = threading.Thread(target=winsound.PlaySound, args=("SystemExclamation", winsound.SND_ALIAS))
        warningWin.focus()

        thread1.start()
    else:
        disconnect_and_close()


def _on_mousewheel(event):
    canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

connection_menu = tk.Menu(menu_bar, tearoff=0)
connection_menu.add_command(
    label="Start Server",
    command=startSocket
)
connection_menu.add_command(
    label="Stop Server",
    command=stopSocket,
    state="disabled"
)
connection_menu.add_command(
    label="Exit",
    command=root.quit
)

menu_bar.add_cascade(
    label="Connection",
    menu=connection_menu
)

othersMenu = tk.Menu(menu_bar, tearoff=0)
othersMenu.add_command(
    label="About", 
    command=about
)
othersMenu.add_command(
    label="Check for Update", 
    command=updateWin
)
menu_bar.add_cascade(
    label="More", 
    menu=othersMenu
)

IPandPORT = ""
title = tk.Label(root, text="IPCom Server", font=("Comic Sans MS", 20, "bold"))
title.pack()
ip_text = tk.Label(root, text="Server is not started yet.", font=("Segoe UI", 10, "bold"))
ip_text.pack(pady=0)

mLog_text = tk.Label(root, text="Messaging Log", font=("Segoe UI", 12, "bold"))
mLog_text.pack(padx=10, pady=10, anchor="nw")

mFrame = tk.Frame(root, highlightbackground="black", highlightthickness=1, height=270, width=570)
mFrame.place(x=12, y=105)
mFrame.pack_propagate(False)

canvas = tk.Canvas(mFrame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(mFrame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

inner_frame = tk.Frame(canvas, )
canvas.create_window((0, 0), window=inner_frame, anchor='nw')

canvas.bind_all("<MouseWheel>", _on_mousewheel)

def add_new_msg(sender, message, isJoin: bool = False, isLeft: bool = False):
    if isJoin:
        sFrame = tk.Frame(inner_frame, highlightbackground="green", highlightthickness=2)
    elif isLeft:
        sFrame = tk.Frame(inner_frame, highlightbackground="red", highlightthickness=2)
    else:
        sFrame = tk.Frame(inner_frame, highlightbackground="black", highlightthickness=1)

    sFrame.pack(anchor="w", side="top", padx=10, pady=2)
    n = tk.Label(sFrame, text=f"{sender}: {message}", wraplength=524, justify="left", font=("Consolas", 9, "bold"))
    n.pack(anchor="w", fill=tk.BOTH)
    inner_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(1.0)

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
                    message = self.client_socket.recv(1024).decode("utf-8")
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
                    add_new_msg("SYSTEM", f"{str(message1).replace('TO SYSTEM===', '')} just left the chat!", isLeft=True)
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
                    add_new_msg("SYSTEM", f"{str(message1).replace('TO SYSTEM===', '')} just joined the chat!", isJoin=True)
                    continue
                if message != "":
                    for client in clients:
                        if client is not self.client_socket:
                            client.send((message).encode("utf-8"))
                    sender, message = str(message).split("||||||!!||||||", 1)
                    add_new_msg(sender, message)
        finally:
            self.client_socket.close()
            for client in clients:
                if client is not self.client_socket:
                    client.send((f"SYSTEM||||||!!||||||{str(message1).replace('TO SYSTEM===', '')} just left the chat!").encode("utf-8"))

            add_new_msg("SYSTEM", f"{str(message1).replace('TO SYSTEM===', '')} just left the chat!", isLeft=True)

    def terminate(self):
        self.terminate_flag.set()        

root.mainloop()
