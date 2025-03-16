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

def render_win(root):
    win_text = tk.Label(text="rah")
    win_text.pack()
    def key_down(event):
        if event.keysym.lower() == "a":
            new_game()
            exit()
    root.bind("<KeyPress>", key_down)

def render_lose(root):
    win_text = tk.Label(text="not rah")
    win_text.pack()
    def key_down(event):
        if event.keysym.lower() == "a":
            new_game()
            exit()
    root.bind("<KeyPress>", key_down)


def new_game():
    root = tk.Tk()
    root.title("HangManager")
    root.attributes("-fullscreen", True)
    root.geometry("1920x1080")
    
    file_path = conn.recv(1024).decode()
    file_dir = os.path.dirname(file_path) + "/"
    file_name = os.path.basename(file_path)

    keyboard_labels = {}
    guessed_letters = []

    guesses_left = tk.IntVar(value = 10)

    dir_frame = tk.Label(root, text=file_dir, font=("Menlo", 15), fg="gray")
    dir_frame.pack()

    file_frame = tk.Label(root, font=("Menlo", 25))
    file_frame.pack()
    
    def censor_filename():
        censored = ""
        for letter in file_name:
            lower = letter.lower()
            if 'a' <= lower <= 'z' and lower not in guessed_letters:
                censored += "☐"
            else:
                censored += letter
        file_frame.config(text=censored)
    censor_filename()

    guesses_left_frame = tk.Label(root, textvariable=guesses_left, font=("Arial", 25))
    guesses_left_frame.pack()

    keyboard = [
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm"
    ]
    
    for row in keyboard:
        outer_frame = tk.Frame(root)
        outer_frame.pack(fill="x")
        row_frame = tk.Frame(outer_frame)
        row_frame.pack()
        for letter in row:
            label = tk.Label(row_frame, text=letter, font=("Menlo", 15), width=3, fg="black", padx=5, pady=5)
            label.pack(side="left", padx=2, pady=2)
            keyboard_labels[letter] = label

    def did_win():
        for letter in file_name:
            lower = letter.lower()
            if 'a' <= lower <= 'z' and lower not in guessed_letters:
                return False
        return True

    def win():
        conn.sendall(b"win")
        root.unbind_all("<KeyPress>")
        render_win(root)
        # do recursion
          
    def lose():
        conn.sendall(b"lose")
        root.unbind_all("<KeyPress>")
        for widget in root.winfo_children():
            widget.destroy()
        render_lose(root)
        
    def key_down(event):
        key = event.keysym.lower()
        
        # check if already included
        if len(key) != 1 or key < 'a' or key > 'z' or key in guessed_letters:
            return
        
        guessed_letters.append(key)
        
        if key in file_name.lower():
            color = "#6ed420" # green
            if did_win():
                win()
        else:
            guesses_left.set(guesses_left.get() - 1)
            if guesses_left.get() == 0:
                lose()
            color = "#d64040" # red
        
        keyboard_labels[key].config(bg=color)
        censor_filename()
        
          
    root.bind("<KeyPress>", key_down)          
    root.mainloop()

new_game()