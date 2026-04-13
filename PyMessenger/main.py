import threading
import keys
import time
from cryptography.hazmat.primitives import serialization
from server import __socket__
from client import __socket_client__

def main():
    print("----CHAT ENCRYPTED----\n")
    priv,pub = keys.gen_dual_key()
    pub_pem = pub.public_bytes(
        encoding= serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    print(pub_pem.decode())
    print("Send this key to the other person!!\n")
    print("Enter other's person public key in a file with a .pem termination\n")
    print("Then type the file path below\n")
    path = input("path:")
    with open(path, "r")as f:
        data = f.read()
    server_pub_pem_key = serialization.load_pem_public_key(data.encode('utf-8'))
    port = int(input("Enter YOUR port to use: "))
    listener_thread = threading.Thread(target=__socket__, args=(port, priv))
    listener_thread.daemon = True
    listener_thread.start()
    
    event = threading.Event()
    sendto_ip = input("Enter other person's ip: ")
    sendto_port = int(input("Enter other person's port: "))
    client_thread = threading.Thread(target=__socket_client__, args=(sendto_ip,sendto_port, server_pub_pem_key, event))
    client_thread.daemon = True
    client_thread.start()

    while not event.is_set():
        time.sleep(1.0)



if __name__ == "__main__":
    main()