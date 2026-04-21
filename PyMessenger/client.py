import socket
import queue
from messages import prepare_message


def __socket_client__(ip: str, port: int, pub, event, send_queue: queue.Queue) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        while True:
            message = send_queue.get()      # Bloquea hasta que haya algo que enviar
            if message == "exit":
                event.set()
                break
            encrypted_message = prepare_message(pub, message)
            sock.sendto(encrypted_message, (ip, port))
    except Exception as e:
        print(f"[error del cliente: {e}]")
    finally:
        sock.close()
