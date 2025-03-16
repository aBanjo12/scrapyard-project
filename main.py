import os
import subprocess
import platform
import socket
import tkinter as tk

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
        subprocess.Popen(
            [ # "pkexec",
                "python3", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

# i hope you like globals
def new_game():
    global keyboard_labels
    global guessed_letters
    global guesses_left
    global file_path
    global file_dir
    global file_name

    file_path = conn.recv(1024).decode()
    file_dir = os.path.dirname(file_path) + "/"
    file_name = os.path.basename(file_path)
    keyboard_labels = {}
    guessed_letters = []
    guesses_left = 10

    for widget in root.winfo_children():
        widget.destroy()

    make_frames_and_keyboard()
    render()

def make_frames_and_keyboard():
    global dir_frame
    global file_frame
    global guesses_left_frame

    dir_frame = tk.Label(root, text=file_dir, font=("Consolas", 15), fg="gray")
    file_frame = tk.Label(root, font=("Consolas", 30))
    guesses_left_frame = tk.Label(root, font=("Arial", 20))

    dir_frame.pack()
    file_frame.pack()
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
            label = tk.Label(row_frame, text=letter, font=("Arial", 15), width=3, fg="black", padx=5, pady=5, cursor="hand2")
            label.pack(side="left", padx=2, pady=2)
            # I HATE PYTHON I HATE PYTHON
            label.bind("<Button-1>", lambda _, l=letter: on_key_down(l))
            keyboard_labels[letter] = label

def render():
    censored = ""
    for letter in file_name:
        lower = letter.lower()
        if 'a' <= lower <= 'z' and lower not in guessed_letters:
            censored += "☐"
        else:
            censored += letter
    file_frame.config(text=censored)

    # also render image here
    guesses_left_frame.config(text="Hearts: " + str(guesses_left))

    if won():
        conn.sendall(b"won")
        new_game()
    elif lost():
        conn.sendall(b"lost")
        new_game()

def lost():
    return guesses_left <= 0

def won():
    for letter in file_name:
        lower = letter.lower()
        if 'a' <= lower <= 'z' and lower not in guessed_letters:
            return False
    return True

def on_key_down(key):
    # check if already included
    if len(key) != 1 or key < 'a' or key > 'z' or key in guessed_letters:
        return

    guessed_letters.append(key)

    if key in file_name.lower():
        color = "#6ed420" # green
    else:
        global guesses_left
        guesses_left -= 1
        color = "#d64040" # red

    keyboard_labels[key].config(bg=color, cursor="arrow")
    render()

launch_deleter()

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        conn.connect(('localhost', 25567))
        break
    except:
        pass

print("Connected")

root = tk.Tk()
root.title("HangManager")
root.geometry("1920x1080")
new_game()
root.bind("<KeyPress>", lambda e: on_key_down(e.keysym.lower()))
root.mainloop()
