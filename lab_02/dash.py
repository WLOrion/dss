import socket
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

st = {}
lck = threading.Lock()

def rcv(ip, p):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, p))
    s.listen()
    while True:
        c, _ = s.accept()
        d = c.recv(4096).decode()
        if d:
            try:
                m = json.loads(d)
                n = m["id"]
                with lck:
                    if n not in st:
                        st[n] = {"c": 0, "lg": [], "ldr": "-", "mtx": "-"}
                    if "c" in m:
                        st[n]["c"] = m["c"]
                    if "msg" in m:
                        st[n]["lg"].insert(0, m["msg"])
                        st[n]["lg"] = st[n]["lg"][:10]
                    if "ldr" in m:
                        st[n]["ldr"] = m["ldr"]
                    if "mtx" in m:
                        st[n]["mtx"] = m["mtx"]
            except:
                pass
        c.close()

class WH(BaseHTTPRequestHandler):
    def log_message(s, fmt, *args):
        pass

    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        with lck:
            h = """
            <html>
            <head>
                <meta http-equiv='refresh' content='1'>
                <style>
                    body { font-family: monospace; background: #111; color: #0f0; padding: 20px; }
                    table { width: 100%; border-collapse: collapse; text-align: left; }
                    th, td { padding: 12px; border: 1px solid #333; }
                    th { background: #222; }
                    .log { font-size: 0.8em; color: #aaa; }
                </style>
            </head>
            <body>
                <h2>MC714 - SISTEMAS DISTRIBUIDOS</h2>
                <table>
                    <tr><th>NO</th><th>LAMPORT (CLK)</th><th>ULTIMAS 10 MENSAGENS</th><th>LIDER</th><th>MUTEX</th></tr>
            """
            for n, d in sorted(st.items()):
                lgs = "<br>".join(d["lg"])
                h += f"<tr><td>{n}</td><td>{d['c']:02d}</td><td class='log'>{lgs}</td><td>{d['ldr']}</td><td>{d['mtx']}</td></tr>"
            h += "</table></body></html>"
        s.wfile.write(h.encode())

if __name__ == "__main__":
    threading.Thread(target=rcv, args=("0.0.0.0", 9368), daemon=True).start()
    s = HTTPServer(("0.0.0.0", 9367), WH)
    s.serve_forever()