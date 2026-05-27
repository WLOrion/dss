import socket
import json
import threading

cb = None

def srv(ip, p):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, p))
    s.listen()
    while True:
        conn, _ = s.accept()
        d = conn.recv(1024).decode()
        if d and cb:
            cb(json.loads(d))
        conn.close()

def init(ip, p, f):
    global cb
    cb = f
    t = threading.Thread(target=srv, args=(ip, p), daemon=True)
    t.start()

def snd(d_ip, d_p, m):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((d_ip, d_p))
        s.send(json.dumps(m).encode())
        s.close()
    except:
        pass