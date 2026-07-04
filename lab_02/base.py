import socket
import json
import threading

cb = None

def srv(ip, p):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, p))
    s.listen()

    print(f"[BASE] Escutando em {ip}:{p}")

    while True:
        conn = None

        try:
            conn, addr = s.accept()

            data = conn.recv(4096)
            if not data:
                continue

            try:
                msg = json.loads(data.decode("utf-8"))
            except Exception as e:
                print(f"[BASE] JSON inválido de {addr}: {e}")
                continue

            print(f"[BASE] RECV <- {addr}: {msg}")

            if cb:
                try:
                    cb(msg)
                except Exception as e:
                    print(f"[BASE] Callback falhou: {e}")

        except Exception as e:
            print(f"[BASE] Erro no servidor: {e}")

        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass


def init(ip, p, f):
    global cb
    cb = f

    threading.Thread(
        target=srv,
        args=(ip, p),
        daemon=True
    ).start()


def snd(d_ip, d_p, m):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((d_ip, d_p))

        data = json.dumps(m).encode("utf-8")
        s.sendall(data)

        print(f"[BASE] SEND -> {d_ip}:{d_p}: {m}")

    except Exception as e:
        print(f"[BASE] SEND ERRO {d_ip}:{d_p}: {e}")

    finally:
        try:
            s.close()
        except:
            pass