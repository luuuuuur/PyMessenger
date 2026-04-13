from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def gen_dual_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_key = private_key.public_key()
    return (private_key, public_key)





#_ , public_key = gen_dual_key()

#pub_pem = public_key.public_bytes(
#    encoding= serialization.Encoding.PEM,
#    format=serialization.PublicFormat.SubjectPublicKeyInfo
#)
#print(pub_pem.decode())


#sender encripts message with its public key
def encrypt(pub_key, message):
    encript_message = pub_key.encrypt(
       message,
       padding.OAEP(
          mgf=padding.MGF1(algorithm=hashes.SHA256()),
          label=None,
          algorithm=hashes.SHA256()
       )
    )
    return encript_message


#reciever decrypts with its private key
def decrypt_message(priv_key,message):
    encrypt_message = priv_key.decrypt(
        message,
       padding.OAEP(
          mgf=padding.MGF1(algorithm=hashes.SHA256()),
          label=None,
          algorithm=hashes.SHA256()
       )
    )
    decoded_message = encrypt_message.decode('utf-8')
    return decoded_message
