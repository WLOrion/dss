import base
import sys
import time
import threading
import random
import csv
import socket
import json

c = 0
l = threading.Lock()
n_id = ""
ip = ""
p = 0
hb = 0
pr = []
d_ip = "127.0.0.1" 
d_p = 9368 

def s_dsh(m_str=""):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((d_ip, d_p))
        d = {"id": n_id, "c": c}
        if m_str:
            d["msg"] = m_str
        s.send(json.dumps(d).encode())
        s.close()
    except:
        pass

def evt():
    global c
    with l:
        c += 1
    return c

def rcv(m):
    global c
    with l:
        c = max(c, m.get("c", 0)) + 1
    lg = f"REC <- [{m['id']}] | M_CLK: {m['c']:02d}"
    print(f"[{n_id}] {lg} | L_CLK: {c:02d}")
    s_dsh(lg)

def snd_m(d_id, dst_ip, dst_p):
    cur = evt()
    m = {"id": n_id, "c": cur}
    base.snd(dst_ip, dst_p, m)
    lg = f"SND -> [{d_id}] | M_CLK: {cur:02d}"
    print(f"[{n_id}] {lg} | L_CLK: {c:02d}")
    s_dsh(lg)

def lp():
    while True:
        time.sleep(hb)
        if pr:
            t = random.choice(pr)
            snd_m(t[0], t[1], t[2])

if __name__ == "__main__":
    n_id = sys.argv[1]
    d_ip = sys.argv[2]
    p = sys.argv[2]

    with open('nodes.csv', 'r') as f:
        r = csv.reader(f)
        for row in r:
            if row[0] == n_id:
                ip = row[1]
                hb = int(row[2])
            else:
                pr.append((row[0], row[1], int(row[2])))
                
    base.init(ip, p, rcv)
    
    threading.Thread(target=lp, daemon=True).start()
        
    while True:
        time.sleep(1)