import socket
import threading
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

st = {}
st_lock = threading.Lock()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

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

                    .on  { color: #4caf50; font-weight: bold; }
                    .off { color: #f44336; font-weight: bold; }
                </style>

                <script>
                    function u() {
                        fetch("/d")
                        .then(r => r.json())
                        .then(d => {
                            let t = "<table><tr><th>ID</th><th>STATUS</th><th>CLK</th><th>LDR</th><th>MTX</th></tr>";
                            let now = Date.now() / 1000;
                            let ids = Object.keys(d).sort((a,b)=>Number(a)-Number(b));

                            for (let i of ids) {
                                let n = d[i];
                                let on = (now - n.ts) < 8;

                                t += `<tr>
                                    <td>${i}</td>
                                    <td>${on ? "<span class='on'>ONLINE</span>" : "<span class='off'>OFFLINE</span>"}</td>
                                    <td>${n.c ?? "-"}</td>
                                    <td>${n.ldr ?? "-"}</td>
                                    <td>${n.mtx ?? "-"}</td>
                                </tr>`;
                            }

                            t += "</table>";
                            document.getElementById("b").innerHTML = t;
                        })
                        .catch(console.error);
                    }

                    setInterval(u, 500);
                </script>
            </head>

            <body onload="u()">
                <h2>Dash (MC714)</h2>
                <div id="b"></div>
            </body>
            </html>"""

            self.wfile.write(h.encode())

        elif self.path == "/d":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            with st_lock:
                data = {k: dict(v) for k, v in st.items()}

            self.wfile.write(json.dumps(data).encode())


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

        try:
            d = c.recv(4096).decode()

            if d:
                j = json.loads(d)
                i = str(j["id"])

                with st_lock:
                    if i not in st:
                        st[i] = {}

                    st[i].update(j)
                    st[i]["ts"] = time.time()

                print(f"[DASH] Atualizacao recebida do Nó {i}")

        except Exception as e:
            print(e)

        finally:
            c.close()


if __name__ == "__main__":
    threading.Thread(target=t_srv, daemon=True).start()

    print("[DASH] Painel Web rodando em http://localhost:9367")

    Server(("0.0.0.0", 9367), H).serve_forever()