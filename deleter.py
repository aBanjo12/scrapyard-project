import socket
import os
import platform
import random

def is_windows():
    return platform.system() == "Windows"

def get_starting_folders():
    if is_windows():
        names = ['/Program Files', '/Program Files (x86)', '/Users', '/Windows', '/ProgramData']
    else:
        names = ['/bin', '/dev', '/etc', '/home', '/lib', '/lib64', '/sbin', '/usr', '/var']
    entries = []
    for entry in os.scandir("/"):
        if entry.path in names:
            entries.append(entry)
    return entries

def get_files(folders):
    random.shuffle(folders)
    for folder in folders:
        new_folders = []
        try:
            all = list(os.scandir(folder))
        except:
            continue
        random.shuffle(all)
        for entry in all:
            if entry.is_symlink():
                continue
            elif entry.is_file():
                yield entry
            elif entry.is_dir():
                new_folders.append(entry)
        if len(new_folders) != 0:
            yield from get_files(new_folders)

def should_skip(path):
    bads = ["cache", "tmp", "temp", "log", "crash", ".config", "debug"]
    for bad in bads:
        if bad in path.lower():
            return True
    file_name = os.path.basename(path)
    if len(file_name) > 30:
        return True
    for letter in file_name:
        if 'a' <= letter <= 'z':
            return False
    # should skip because no letters
    return True

def get_random_file():
    iter = get_files(get_starting_folders())
    first_50 = []
    while len(first_50) < 50:
        file = next(iter)
        if not should_skip(file.path):
            first_50.append(file)
    return random.choice(first_50)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 25567))
    server_socket.listen(1)

    conn, address = server_socket.accept()
    print("Connection from: " + str(address))


    file_path = ""

    while True:
        # file = get_random_file()
        data = conn.recv(1024).decode()
        if not data:
            # client closed it
            conn.close()
            break
        elif data == "request_file":
            file_path = get_random_file().path
            conn.sendall(file_path.encode())
        elif data == "win":
            print("WIN")
        elif data == "lose_safe":
            print("LOSE but no delete")
        elif data == "lose":
            print("LOSE and deleting " + file_path)
            try:
                os.remove(file_path)
                print("Removed, probably")
                conn.sendall(b"removed")
            except:
                print("Failed to remove")
                conn.sendall(b"failed")
        else:
            print("Got weird data: " + data)

    conn.close()
    print("Server closed!")

start_server()
