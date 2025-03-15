import os
import subprocess
import platform
import socket
import tkinter as tk
from tkinter import *
import re

guess_count = 10
guessed_chars = []
file_path = ""

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

def build_ui(file_name):
    root = tk.Tk()
    
    def key_down(event):
        key = event.keysym.lower()
        if len(key) == 1 and 'a' <= key <= 'z':
            guessed_chars.append(key)
    
    keyboard = [
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm"
    ]
    
    letter_elements = {}
    
    # keyboard (colors for debug)
    for row in keyboard:
        outer_frame = tk.Frame(root, bg="blue")
        outer_frame.pack(fill="x", pady=5)
        row_frame = tk.Frame(outer_frame, bg="red")
        row_frame.pack(pady=5)
        for letter in row:
            label = tk.Label(row_frame, text=letter)
            label.pack(side="left", padx=5, pady=5)
            letter_elements[letter] = label

    # Center the frame within the root window
    # frame.grid_columnconfigure(0, weight=1)
    # frame.grid_columnconfigure(1, weight=1)
    # frame.grid_columnconfigure(2, weight=1)

    # l = Label(root, textvariable = current)
    # l.pack()

    root.title("Game Name Here")
    # label = tk.Label(root, text=file_name, font=("Arial", 14))
    # label.pack(pady=20)
    root.bind("<KeyPress>", key_down)
    root.mainloop()


def main():
    launch_deleter()
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            conn.connect(('localhost', 25567))
            break
        except:
            pass
    print("Connected")
    file_path = conn.recv(1024).decode()
    file_name = os.path.basename(file_path)
    print(file_name)
    build_ui(file_name)
    #print("hang.py recieved " + data)
    

if __name__ == "__main__":
    main()