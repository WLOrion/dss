import base
import sys
import time
import threading
import csv
import socket
import json
import random

n_id = 0
ip = ""
p = 0
hb = 0
pr = []
c = 0
s = 0 
r_c = 0
rep = 0
exp = 0
q = []
lck = threading.Lock()

d_ip = "127.0.0.1" 
d_p = 9368

def s_dsh(msg=None, mtx=None):
    try:
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.connect((d_ip, d_p))
        d = {"id": str(n_id)}
        if msg: d["msg"] = msg
        if mtx: d["mtx"] = mtx
        skt.send(json.dumps(d).encode())
        skt.close()
    except:
        pass

def rcv(m):
    global c, s, rep
    
    t = m["t"]
    s_id = int(m["id"])
    m_c = m["c"]
    
    with lck:
        c = max(c, m_c) + 1
        
    lg = f"REC <- [{s_id}] | {t}"
    print(f"[{n_id}] {lg}")
    s_dsh(msg=lg)
    
    if t == "REQ":
        df = False
        with lck:
            if s == 2:
                df = True
            elif s == 1:
                if (r_c, n_id) < (m_c, s_id):
                    df = True
        
        if df:
            with lck:
                q.append(s_id)
        else:
            snd(s_id, "REP")
            
    elif t == "REP":
        with lck:
            rep += 1
            if rep >= exp and s == 1:
                s = 2
                m_st = "NA_REGIAO_CRITICA"
                print(f"[{n_id}] {m_st}")
                s_dsh(mtx=m_st)
                threading.Thread(target=use_rc).start()

def snd(d_id, t):
    global c
    
    with lck:
        c += 1
        cur = c
        
    for r in pr:
        if r[0] == d_id:
            m = {"id": n_id, "t": t, "c": cur}
            base.snd(r[1], r[2], m)
            if t != "REP":
                lg = f"SND -> [{d_id}] | {t}"
                print(f"[{n_id}] {lg}")
                s_dsh(msg=lg)
            break

def b_req():
    global s, r_c, rep, c, exp
    
    with lck:
        s = 1
        c += 1
        r_c = c
        rep = 0
        exp = 9999
    
    m_st = "AGUARDANDO"
    print(f"[{n_id}] {m_st}")
    s_dsh(mtx=m_st)
    
    a = 0
    for x in pr:
        try:
            skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt.settimeout(0.5)
            skt.connect((x[1], x[2]))
            skt.close()
            a += 1
            snd(x[0], "REQ")
        except:
            pass
            
    with lck:
        exp = a
        if rep >= exp and s == 1:
            s = 2
            m_st = "NA_REGIAO_CRITICA"
            print(f"[{n_id}] {m_st}")
            s_dsh(mtx=m_st)
            threading.Thread(target=use_rc).start()

def use_rc():
    global s
    
    time.sleep(5)
    
    with lck:
        s = 0
        m_st = "LIBERADO"
        print(f"[{n_id}] {m_st}")
        s_dsh(mtx=m_st)

        fila_pendentes = list(q)
        q.clear()

    for x in fila_pendentes:
        snd(x, "REP")

def lp():
    while True:
        time.sleep(hb * 3)
        with lck:
            cur_s = s
        if cur_s == 0 and random.random() > 0.5:
            b_req()

if __name__ == "__main__":
    n_id = int(sys.argv[1])
    d_ip = sys.argv[2]
    p = int(sys.argv[3])

    with open("nodes.csv") as f:
        r = csv.reader(f)
        for row in r:
            if int(row[0]) == n_id:
                ip = row[1]
                hb = int(row[-1])
            else:
                pr.append((int(row[0]), row[1], p))
                
    base.init(ip, p, rcv)
    time.sleep(2)
    
    threading.Thread(target=lp, daemon=True).start()
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass