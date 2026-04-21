import socket
import queue
import keys


def __socket__(port: int, priv, msg_queue: queue.Queue) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("0.0.0.0", port))
        while True:
            encrypted_data, addr = sock.recvfrom(1250)
            data = keys.decrypt_message(priv, encrypted_data)
            msg_queue.put(data)
    except Exception as e:
        msg_queue.put(f"[error del servidor: {e}]")
    finally:
        sock.close()
