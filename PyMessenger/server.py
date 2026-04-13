import socket
import keys

def __socket__(port, priv):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("0.0.0.0", port))
        while True:
            encrypted_data , addr = sock.recvfrom(1250)
            data = keys.decrypt_message(priv, encrypted_data)
            print(f"Sender:{data}")
    except Exception as e:
        print("Error: "+ str(e))


