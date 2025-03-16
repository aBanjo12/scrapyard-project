import os
import subprocess
import platform
import socket
import tkinter as tk
import time

def path():
    return os.path.dirname(os.path.realpath(__file__))

def is_windows():
    return platform.system() == "Windows"

def launch_deleter():
    deleter_path = path() + "/deleter.py"
    if is_windows():
        # todo: normal thing for windows
        subprocess.Popen(["powershell", "Start-Process", "python", "-ArgumentList", "'" + deleter_path + "'", "-Verb", "RunAs"])
    else:
        if fun_mode:
            subprocess.Popen(["pkexec", "python3", deleter_path])
        else:
            subprocess.Popen(["python3", deleter_path])

# todo update
lose_taunt_list = ["lmao noob"]
win_message_list = ["you win!"]
green = "#6ed420"
red = "#d64040"

def start_app():
    global conn
    global fun_mode
    
    tk.Label(root, text="Play fun mode?", bg="white")
    tk.Label(root, text="Fun mode means that your ", bg="white")
    # ask for fun mode
    
    fun_mode = False
    
    launch_deleter()

    start = time.time()
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            conn.connect(('localhost', 25567))
            break
        except:
            if time.time() - start > 5:
                raise Exception("Couldn't connect to socket")

    print("Connected")
    # after connected:
    root.bind("<KeyPress>", lambda e: on_key_down(e.keysym.lower()))
    
    new_game()

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

    dir_label = tk.Label(root, text=file_dir, font=("Consolas", 15), fg="gray", bg="white")
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
    dino_image = tk.PhotoImage(file=path()+"/dino/"+name+".png")
    root.img=dino_image
    image_label.config(image=root.img)
    guesses_left_label.config(text="Hearts: " + str(guesses_left))

    if won():
        conn.sendall(b"win")
        label = tk.Button(root, text="New game", command=new_game)
        label.pack(pady=10)
        orph_label = tk.Label(text="You saved Orpheous! :)", font=("Arial", 20), bg="white")
        orph_label.pack(pady=10)


    elif lost():
        if fun_mode:
            conn.sendall(b"lose")
        else:
            conn.sendall(b"lose_safe")
            
        orph_label = tk.Label(text="You killed Orpheous :(", font=("Arial", 20), bg="white")
        orph_label.pack(pady=10)
        deleting_file_label = tk.Label(root, text="deleted " + file_path, fg=red, bg="white", font=("Arial", 20))
        deleting_file_label.pack()
        label = tk.Button(root, text="New game", command=new_game)
        label.pack(pady=10)

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
