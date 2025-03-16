import os
import subprocess
import platform
import socket
import tkinter as tk
import re

def is_windows():
    return platform.system() == "Windows"

def launch_deleter():
    path = os.path.dirname(os.path.realpath(__file__)) + "/deleter.py"
    if is_windows():
        subprocess.Popen(
            ["powershell", "Start-Process", "python", "-ArgumentList", "'" + path + "'", "-Verb", "RunAs"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    else:
        subprocess.Popen([
            # "pkexec",
            "python3", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

launch_deleter()

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        conn.connect(('localhost', 25567))
        break
    except:
        pass

print("Connected")

def new_game():
    root = tk.Tk()
    root.title("HangManager")
    root.attributes("-fullscreen", True)
    root.geometry("1920x1080")
    
    file_path = conn.recv(1024).decode()
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    # for widget in root.winfo_children():
    #     widget.destroy()

    dir_frame = tk.Label(root, text=file_dir, font=("Arial", 15), fg="gray")
    dir_frame.pack()

    file_frame = tk.Label(root, text=file_name, font=("Arial", 25))
    file_frame.pack()

    keyboard = [
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm"
    ]
    
    keyboard_labels = {}
    guessed_letters = []
    
    for row in keyboard:
        outer_frame = tk.Frame(root)
        outer_frame.pack(fill="x")
        row_frame = tk.Frame(outer_frame)
        row_frame.pack()
        for letter in row:
            label = tk.Label(row_frame, text=letter, font=("Arial", 15), fg="black")
            label.pack(side="left", padx=10, pady=5)
            keyboard_labels[letter] = label
            
    def key_down(event):
        key = event.keysym.lower()
        if len(key) == 1 and 'a' <= key <= 'z':
            # check if already included
            if key not in guessed_letters:
                guessed_letters.append(key)
                color = "green" if key in file_name else "red"
                keyboard_labels[key].config(fg=color)
      
    root.bind("<KeyPress>", key_down)          
    root.mainloop()

new_game()

