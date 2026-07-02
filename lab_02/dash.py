import socket
import threading
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

st = {}

class H(BaseHTTPRequestHandler):
    def do_GET(s):
        if s.path == "/":
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            
            h = """<!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: monospace; background: #1e1e1e; color: #fff; padding: 20px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }
                    th, td { border: 1px solid #444; padding: 10px; text-align: center; overflow: hidden; }
                    th { background: #333; }
                    th:nth-child(1) { width: 10%; } 
                    th:nth-child(2) { width: 20%; } 
                    th:nth-child(3) { width: 20%; } 
                    th:nth-child(4) { width: 25%; } 
                    th:nth-child(5) { width: 25%; } 
                    
                    .on { color: #4caf50; font-weight: bold; }
                    .off { color: #f44336; font-weight: bold; }
                </style>
                <script>
                    function u() {
                        fetch('/d')
                        .then(r => r.json())
                        .then(d => {
                            let t = "<table><tr><th>ID</th><th>STATUS</th><th>CLK</th><th>LDR</th><th>MTX</th></tr>";
                            let k = Object.keys(d).sort();
                            let now = Date.now() / 1000;
                            
                            for (let i of k) {
                                let n = d[i];
                                let is_on = (now - n.ts) < 8;
                                let status_html = is_on ? "<span class='on'>ONLINE</span>" : "<span class='off'>OFFLINE</span>";
                                
                                t += `<tr>
                                    <td>${i}</td>
                                    <td>${status_html}</td>
                                    <td>${n.c || "-"}</td>
                                    <td>${n.ldr || "-"}</td>
                                    <td>${n.mtx || "-"}</td>
                                </tr>`;
                            }
                            t += "</table>";
                            document.getElementById("b").innerHTML = t;
                        });
                    }
                    setInterval(u, 500);
                </script>
            </head>
            <body onload="u()">
                <h2>Dash (MC714)</h2>
                <div id="b"></div>
            </body>
            </html>"""
            s.wfile.write(h.encode())
            
        elif s.path == "/d":
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            s.wfile.write(json.dumps(st).encode())

class Server(HTTPServer):
    allow_reuse_address = True

def t_srv():
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    skt.bind(("0.0.0.0", 9368))
    skt.listen()
    print("[DASH] Escutando eventos TCP na porta 9368...")
    while True:
        c, _ = skt.accept()
        d = c.recv(1024).decode()
        if d:
            try:
                j = json.loads(d)
                i = j["id"]
                if i not in st:
                    st[i] = {}
                for k in j:
                    st[i][k] = j[k]
                st[i]["ts"] = time.time()
                print(f"[DASH] Atualizacao recebida do Nó {i}")
            except:
                pass
        c.close()

if __name__ == "__main__":
    threading.Thread(target=t_srv, daemon=True).start()
    print("[DASH] Painel Web rodando em http://localhost:9367")
    Server(("0.0.0.0", 9367), H).serve_forever()