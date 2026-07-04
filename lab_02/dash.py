import socket
import threading
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

st = {}
lck = threading.Lock()

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            html = """
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: monospace; background:#111; color:#fff; }
table { width:100%; border-collapse: collapse; }
th, td { border:1px solid #444; padding:8px; text-align:center; }
.on { color:#0f0; }
.off { color:#f33; }
</style>
<script>
function upd(){
    fetch('/d')
    .then(r => r.json())
    .then(d => {
        let now = Date.now()/1000;
        let html = "<table><tr><th>ID</th><th>STATUS</th><th>CLK</th><th>LDR</th><th>MTX</th></tr>";

        Object.keys(d).sort((a,b)=>a-b).forEach(i=>{
            let n = d[i];
            let on = (now - n.ts) < 10;

            html += `<tr>
                <td>${i}</td>
                <td>${on ? "<span class='on'>ONLINE</span>" : "<span class='off'>OFFLINE</span>"}</td>
                <td>${on ? (n.c ?? "-") : "-"}</td>
                <td>${on ? (n.ldr ?? "-") : "-"}</td>
                <td>${on ? (n.mtx ?? "-") : "-"}</td>
            </tr>`;
        });

        html += "</table>";
        document.getElementById("x").innerHTML = html;
    });
}
setInterval(upd, 1000);
</script>
</head>
<body onload="upd()">
<h2>Dash MC714</h2>
<div id="x"></div>
</body>
</html>
"""
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        elif self.path == "/d":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            with lck:
                self.wfile.write(json.dumps(st).encode())

def hndl(c):
    try:
        raw = c.recv(4096)
        if raw:
            msg = json.loads(raw.decode(errors="ignore"))
            i = str(msg.get("id"))
            
            with lck:
                if i not in st:
                    st[i] = {}
                if "ldr" not in msg:
                    st[i]["ldr"] = "-"
                st[i].update(msg)
                st[i]["ts"] = time.time()
    except:
        pass
    finally:
        c.close()

def tcp_srv():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 9368))
    s.listen(100)

    print("[DASH] TCP ON 9368")

    while True:
        c, _ = s.accept()
        threading.Thread(target=hndl, args=(c,), daemon=True).start()

if __name__ == "__main__":
    threading.Thread(target=tcp_srv, daemon=True).start()
    HTTPServer(("0.0.0.0", 9367), H).serve_forever()