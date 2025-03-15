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
        names =  ['/bin', '/boot', '/dev', '/etc', '/home', '/lib', '/lib64', '/proc', '/sbin', '/sys', '/usr', '/var']
    entries = []
    for entry in os.scandir("/"):
        if entry.path in names:
            entries.append(entry)
    return entries

def get_files(folders):
    random.shuffle(folders)
    new_entries = []
    for folder in folders:
        all = list(os.scandir(folder))
        random.shuffle(all)
        for entry in all:
            if entry.is_symlink():
                continue
            elif entry.is_file():
                yield entry
            elif entry.is_dir():
                new_entries.append(entry)
    if len(new_entries) != 0:
        yield from get_files(new_entries)

def should_skip(path):
    bads = ["cache", "tmp", ".config"]
    for bad in bads:
        if bad in path:
            return True
    return False

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
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server_socket.bind(('localhost', 25567))
    server_socket.listen(1)

    conn, address = server_socket.accept()
    print("Connection from: " + str(address))
    while True:
        # file = get_random_file()
        # conn.sendall(get_random_file().path.encode())
        conn.sendall(b"/bin/landon/this_is_a_real_file.real")
        while True:
            data = conn.recv(1024).decode()
            if not data:
                # client closed it
                conn.close()
                return
            elif data == "win":
                continue
            elif data == "lose":
                # os.remove(entry.path)
                # if os.path.exists(entry.path):
                    # print("Failed to remove")
                pass
            else:
                print("Weird!")

start_server()