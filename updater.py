import os
import tkinter as tk
from tkinter import messagebox
import urllib.error
from urllib.request import urlopen
from threading import Thread
import json
import time

ipcom_icon = "./Assets/IPCom.ico"

with open("data.json", "r") as f:
    current_version = json.load(f)["version"]
        

def updateWin():
    global download_thread_killed, ipcom_running_check

    download_thread_killed = False
    ipcom_running_check = False

    def close_ipcoms():
        os.popen("taskkill /F /IM \"IPCom.exe\"")
        os.popen("taskkill /F /IM \"IPCom Server.exe\"")
    
    def close_ipcoms_thread():
        global ipcom_running_check

        while True:
            if ipcom_running_check:
                close_ipcoms()
                time.sleep(7)
            else:
                ipcom_running_check = False
                break

    def on_closing_on_updating():
        global download_thread_killed

        if messagebox.askyesno("IPCom Updater", "Do you really want to Close the Updater?\nClosing the Updater will cause you to lose your update progress!"):
            download_thread_killed = True
            root.quit()

    def on_closing_on_update_fails():
        global download_thread_killed

        download_thread_killed = True
        root.quit()
    
    def on_closing_on_update_finished():
        root.quit()

    root = tk.Tk()
    root.title("IPCom Updater")
    positionRight = int(root.winfo_screenwidth()/2 - 430/2)
    positionDown = int(root.winfo_screenheight()/2 - 138/2)
    root.geometry(f"430x138+{positionRight}+{positionDown - 50}")
    root.resizable(0, 0)
    root.wm_attributes("-topmost", True)
    root.pack_propagate(True)
    root.wm_iconbitmap(ipcom_icon)


    def download_thread(obj, downloads, nVersion):
        global ipcom_running_check
        
        root.protocol("WM_DELETE_WINDOW", on_closing_on_updating)
        for i, download in enumerate(downloads):
            ipcom_running_check = True
            Thread(target=close_ipcoms_thread, daemon=True).start()
            if download_thread_killed == True:
                ipcom_running_check = False
                return
            obj.config(state="normal")
            obj.delete(0, "end")
            obj.insert(0, f"({i+1}/{len(downloads)}) Downloading...")
            obj.config(state="readonly")

            try:
                response = urlopen(download['url'])
            except urllib.error.URLError:
                obj.config(state="normal")
                obj.delete(0, "end")
                obj.insert(0, f"Network Error! Please try again later!")
                obj.config(state="readonly")
                root.protocol("WM_DELETE_WINDOW", on_closing_on_update_fails)
                return
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            fName, fExtension = str(download['name']).split('.', -1)[0], str(download['name']).split('.', -1)[1]
            fName.replace("-", " ")
            with open(f"{fName}_updateCache.{fExtension}", "wb") as file:
                while True:
                    if download_thread_killed == True:
                        ipcom_running_check = False
                        return
                    data = response.read(8192)
                    if not data:
                        file.close()
                        break
                    downloaded_size += len(data)
                    file.write(data)
                    update_progress(obj, f"({i + 1}/{len(downloads)})", total_size, downloaded_size)
            close_ipcoms()
            if os.path.exists(download['name']):
                if "updater" in str(download['name']).lower():
                    os.rename(f"{fName}_updateCache.{fExtension}", f"{fName}_.{fExtension}")
                else:
                    os.remove(download['name'])
                    os.rename(f"{fName}_updateCache.{fExtension}", f"{fName}.{fExtension}")
            else:
                os.rename(f"{fName}_updateCache.{fExtension}", f"{fName}.{fExtension}")

        obj.config(state="normal")
        obj.delete(0, "end")
        obj.insert(0, f"Update Download Completed!")
        obj.config(state="readonly")

        root.wm_attributes("-topmost", False)

        with open("updates.json", 'w') as f:
            json.dump({}, f, indent=4)
        with open("data.json", "r") as f:
            dd = json.load(f)
        dd['version'] = nVersion
        with open("data.json", 'w') as f:
            json.dump(dd, f, indent=4)
        root.protocol("WM_DELETE_WINDOW", on_closing_on_update_finished)
        ipcom_running_check = False
        messagebox.showinfo("IPCom Updater", f"IPCom v{nVersion} has been installed! You may close the Updater now!")
        

    def update_progress(obj, index, total_size, downloaded_size):
        percent = (downloaded_size / total_size) * 100
        obj.config(state="normal")
        obj.delete(0, "end")
        obj.insert(0, f"{index} Writing... {percent:.2f}%")
        obj.config(state="readonly")
    
    msgLabel = tk.Label(root, text="IPCom Updater", font=('Comic Sans MS', 20, "bold"))
    msgLabel.pack()

    current_version_label = tk.Label(root, text=f"Running Version: {current_version}", font=("Segoe UI", 10))
    current_version_label.pack(padx=10, pady=5, anchor="nw")

    status_label = tk.Label(root, text="Status:", font=("Segoe UI", 10))
    status_label.pack(padx=10, side="left", anchor="nw")

    status_entry = tk.Entry(root, state="readonly", font=("consolas", 10), width=40, readonlybackground="white")
    status_entry.pack(pady=3, side="left", anchor="nw")

    status_entry.config(state="normal")
    status_entry.insert(0, "Searching for Update...")
    status_entry.config(state="readonly")

    def check_for_update():
        with open("updates.json", 'r') as f:
            data = json.load(f)
        if data != {} and 'status' in data and data['status'] == "available":
            downloads_list = data['download']

            status_entry.config(state="normal")
            status_entry.delete(0, "end")
            status_entry.insert(0, "Update Available!")
            status_entry.config(state="readonly")

            Thread(target=download_thread, args=(status_entry, downloads_list, data['version']), daemon=True).start()

        else:
            status_entry.config(state="normal")
            status_entry.delete(0, "end")
            status_entry.insert(0, "You are up to date!")
            status_entry.config(state="readonly")

    Thread(target=check_for_update, daemon=True).start()
    root.update_idletasks()
    root.mainloop()

if __name__ == "__main__":
    updateWin()

