import os
import subprocess
import platform
import socket
import tkinter as tk
import time
import random

def path():
    return os.path.dirname(os.path.realpath(__file__))

def is_windows():
    return platform.system() == "Windows"

def launch_deleter():
    deleter_path = path() + "/deleter.py"
    try:
        if is_windows():
            if fun_mode:
                subprocess.Popen(["powershell", "Start-Process", "python", "-ArgumentList", "'" + deleter_path + "'", "-Verb", "RunAs"])
            else:
                subprocess.Popen(["python3", deleter_path])
        else:
            if fun_mode:
                subprocess.Popen(["pkexec", "python3", deleter_path])
            else:
                subprocess.Popen(["python3", deleter_path])
    except Exception as e:
        print("Failed to launch server:")
        print(e)

lose_message_list = ["You killed Orpheous :(", "Guess you didn't need it anyway!", "Say goodbye to your file!"]
win_message_list = ["You saved Orpheous :)", "Your file lives... for now", "Nice job, computer expert!"]
green = "#6ed420"
red = "#d64040"

def start_app():
    def choose_fun(selection):
        global fun_mode
        global conn

        fun_mode = selection
        launch_deleter()

        start = time.time()
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                conn.connect(('localhost', 25567))
                break
            except:
                if time.time() - start > 2:
                    raise Exception("Couldn't connect to socket")

        print("Client connected")
        # after connected:
        root.bind("<KeyPress>", lambda e: on_key_down(e.keysym.lower()))

        new_game()

    tk.Label(root, text="Welcome to HangManager!", font=("Arial", 25), bg="white").pack(pady=50)

    def paragraph(text):
        tk.Label(root, text=text, font=("Arial", 12), wraplength=1000, bg="white").pack(pady=15)

    paragraph("A file on your computer will be chosen at random.")
    paragraph("It's just like Hangman, but instead of guessing an English phrase, you need to guess the name of the file. You'll enter letters that you think it contains. If you enter ten bad letters, you lose.")
    paragraph("Fun mode means that if you fail to guess a file, it'll be deleted from your computer. Play at your own risk!")

    outer_frame = tk.Frame(root, bg="white")
    outer_frame.pack(fill="x")
    row_frame = tk.Frame(outer_frame, bg="white")
    row_frame.pack(pady=30)

    tk.Button(row_frame, text="Safe mode", command=lambda: choose_fun(False)).pack(side="left", padx=5, pady=5)
    tk.Button(row_frame, text="Fun mode", command=lambda: choose_fun(True)).pack(side="left", padx=5, pady=5)
    # ask for fun mode

# i hope you like globals
def new_game():
    global keyboard_labels
    global guessed_letters
    global guesses_left
    global file_path
    global file_dir
    global file_name

    conn.sendall(b"request_file")
    file_path = conn.recv(1024).decode().replace("\\", "/")
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
    global dir_label
    global file_label
    global image_label
    global guesses_left_label

    dir_label = tk.Label(root, text=file_dir, font=("Consolas", 15), wraplength=1000, fg="gray", bg="white")
    file_label = tk.Label(root, font=("Consolas", 30), bg="white")
    image_label = tk.Label(root, bg="white")
    guesses_left_label = tk.Label(root, font=("Arial", 20), bg="white")

    dir_label.pack()
    file_label.pack()
    image_label.pack()
    guesses_left_label.pack()

    keyboard = [
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm"
    ]

    for row in keyboard:
        outer_frame = tk.Frame(root, bg="white")
        outer_frame.pack(fill="x")
        row_frame = tk.Frame(outer_frame, bg="white")
        row_frame.pack()
        for letter in row:
            label = tk.Label(row_frame, text=letter, font=("Arial", 15), width=3, fg="black", padx=5, pady=5, cursor="hand2")
            label.pack(side="left", padx=2, pady=2)
            # I HATE PYTHON I HATE PYTHON
            label.bind("<Button-1>", lambda _, l=letter: on_key_down(l))
            keyboard_labels[letter] = label

def render():
    if won() or lost():
        censored = file_name
    else:
        censored = ""
        for letter in file_name:
            lower = letter.lower()
            if 'a' <= lower <= 'z' and lower not in guessed_letters:
                censored += "☐"
            else:
                censored += letter


    file_label.config(text=censored)

    if won():
        name="party"
    else:
        name=str(guesses_left)

    global dino_image # stop it from being garbage collected
    dino_image = tk.PhotoImage(file=path()+"/dino/"+name+".png")
    image_label.config(image=dino_image)
    guesses_left_label.config(text="Hearts: " + str(guesses_left))

    if won():
        conn.sendall(b"win")

        file_label.config(fg=green)
        orph_label = tk.Label(text=random.choice(win_message_list), font=("Arial", 20), bg="white")
        orph_label.pack(pady=30)
    elif lost():
        if fun_mode:
            conn.sendall(b"lose")
        else:
            conn.sendall(b"lose_safe")

        file_label.config(fg=red)
        orph_label = tk.Label(text=random.choice(lose_message_list), font=("Arial", 20), bg="white")
        orph_label.pack(pady=30)

        if fun_mode:
            status = conn.recv(1024).decode()
            if status == "removed":
                text = "Deleted " + file_path
            else:
                text = "Couldn't delete this file, oops"
        else:
            text = "Didn't actually delete the file"

        deleting_file_label = tk.Label(root, text=text, fg=red, font=("Arial", 15), wraplength=1000, bg="white")
        deleting_file_label.pack()
    else:
        return

    # if won or lost:
    label = tk.Button(root, text="New game", command=new_game, font=("Arial", 15), padx=10, pady=5)
    label.pack(pady=15)

def lost():
    return guesses_left <= 0

def won():
    for letter in file_name:
        lower = letter.lower()
        if 'a' <= lower <= 'z' and lower not in guessed_letters:
            return False
    return True

def on_key_down(key):
    if won() or lost():
        return

    # check if already included
    if len(key) != 1 or key < 'a' or key > 'z' or key in guessed_letters:
        return

    guessed_letters.append(key)

    if key in file_name.lower():
        color = green
    else:
        global guesses_left
        guesses_left -= 1
        color = red

    keyboard_labels[key].config(bg=color, cursor="arrow")
    render()

root = tk.Tk()
root.title("HangManager")
root.geometry("1920x1080")
root.configure(bg="white")
start_app()
root.mainloop()
