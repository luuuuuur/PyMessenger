import socket
from messages import prepare_message
def __socket_client__(ip, port, pub, event):
    flag = False
    while flag != True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = input("You: \n")
        if message == "exit":
            flag = True
            event.set()
            break
        encrypted_message = prepare_message(pub, message)
        sock.sendto(encrypted_message, (ip, port))
        sock.close()
