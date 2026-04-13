import keys

def prepare_message(pub,message):
    encrypted_message = keys.encrypt(pub, message.encode('utf-8'))
    return encrypted_message


def recv_encrypted_message(priv,message):
    decrypted_message = keys.decrypt_message(priv, message)
    return decrypted_message
