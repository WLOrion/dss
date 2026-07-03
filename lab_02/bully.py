import base
import sys
import time
import threading
import csv
import socket
import json

n_id = 0
ip = ""
p = 0
hb = 0
pr = []
ldr = 0
elc = False
lck = threading.Lock()
ok_r = False
last_hbt = time.time()

d_ip = "127.0.0.1" 
d_p = 9368

def s_dsh(msg=None, l_id=None):
    try:
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.connect((d_ip, d_p))
        d = {"id": str(n_id)}
        if msg: d["msg"] = msg
        if l_id is not None: d["ldr"] = str(l_id)
        skt.send(json.dumps(d).encode())
        skt.close()
    except:
        pass

def rcv(m):
    global ldr, elc, ok_r, last_hbt
    t = m["t"]
    s = int(m["id"])

    if t != "HBT": 
        lg = f"REC <- [{s}] | {t}"
        print(f"[{n_id}] {lg}")
        s_dsh(msg=lg)
    
    if t == "HBT":
        if s == ldr:
            last_hbt = time.time()
    elif t == "ELC":
        snd(s, "OK")
        with lck:
            if not elc:
                threading.Thread(target=strt).start()
    elif t == "OK":
        ok_r = True
    elif t == "COR":
        ldr = s
        elc = False
        last_hbt = time.time()
        lg_ldr = f"LIDER: {ldr}"
        print(f"[{n_id}] {lg_ldr}")
        s_dsh(msg=lg_ldr, l_id=ldr)

def snd(d_id, t):
    for r in pr:
        if r[0] == d_id:
            m = {"id": n_id, "t": t}
            base.snd(r[1], r[2], m)
            if t not in ["OK", "HBT"]:
                lg = f"SND -> [{d_id}] | {t}"
                print(f"[{n_id}] {lg}")
                s_dsh(msg=lg)
            break

def strt():
    global elc, ok_r, ldr, last_hbt
    with lck:
        elc = True
        ok_r = False
    
    h = [x for x in pr if x[0] > n_id]
    
    if not h:
        ldr = n_id
        elc = False
        last_hbt = time.time()
        lg_ldr = f"LIDER: {ldr} (EU)"
        print(f"[{n_id}] {lg_ldr}")
        s_dsh(msg=lg_ldr, l_id=ldr)
        for x in pr:
            if x[0] < n_id:
                snd(x[0], "COR")
        return

    for x in h:
        snd(x[0], "ELC")
    
    time.sleep(2) 
    
    if not ok_r:
        ldr = n_id
        elc = False
        last_hbt = time.time()
        lg_ldr = f"LIDER: {ldr} (EU)"
        print(f"[{n_id}] {lg_ldr}")
        s_dsh(msg=lg_ldr, l_id=ldr)
        for x in pr:
            if x[0] < n_id:
                snd(x[0], "COR")

def monitor_lider():
    global last_hbt
    while True:
        time.sleep(hb)
        if ldr == n_id:
            for x in pr:
                if x[0] != n_id:
                    snd(x[0], "HBT")
        else:
            if not elc and ldr != 0:
                if time.time() - last_hbt > (hb * 3):
                    lg = "! LIDER CAIU ! Iniciando eleicao..."
                    print(f"[{n_id}] {lg}")
                    s_dsh(msg=lg, l_id="OFFLINE")
                    threading.Thread(target=strt).start()

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
    time.sleep(2)
    
    if n_id == 1:
        threading.Thread(target=strt).start()
        
    threading.Thread(target=monitor_lider, daemon=True).start()
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass