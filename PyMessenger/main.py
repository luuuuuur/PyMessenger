import tkinter as tk
import queue
import threading
import datetime
from cryptography.hazmat.primitives import serialization
from keys import gen_dual_key
from server import __socket__
from client import __socket_client__

msg_queue:  queue.Queue = queue.Queue()
send_queue: queue.Queue = queue.Queue()

_priv_key = None
_pub_pem:  bytes = b""

mainwindow = tk.Tk()
mainwindow.title("PyMessage")
mainwindow.geometry("820x700")
mainwindow.resizable(True, True)
mainwindow.configure(bg="#f5f5f0")


setup_frame = tk.Frame(mainwindow, bg="#f5f5f0")
setup_frame.pack(fill="both", expand=True, padx=60, pady=40)

tk.Label(
    setup_frame,
    text="PyMessage",
    font=("Courier", 22, "bold"),
    bg="#f5f5f0",
).grid(row=0, column=0, columnspan=2, pady=(0, 6))

tk.Label(
    setup_frame,
    text="mensajería privada peer-to-peer",
    font=("Courier", 9),
    fg="gray",
    bg="#f5f5f0",
).grid(row=1, column=0, columnspan=2, pady=(0, 24))


tk.Label(
    setup_frame,
    text="1. genera tu clave pública y compártela con el peer",
    font=("Courier", 9),
    fg="gray",
    bg="#f5f5f0",
    anchor="w",
).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 6))

tk.Button(
    setup_frame,
    text="generar clave →",
    font=("Courier", 10),
    relief="solid",
    bd=1,
    padx=10,
    pady=3,
    command=lambda: generate_key(),
).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 8))


pub_key_display = tk.Text(
    setup_frame,
    height=5,
    font=("Courier", 7),
    fg="#555",
    bg="#f0f0eb",
    relief="solid",
    bd=1,
    wrap="char",
    state="disabled",
)
pub_key_display.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 4))

copy_btn = tk.Button(
    setup_frame,
    text="copiar clave",
    font=("Courier", 9),
    relief="solid",
    bd=1,
    padx=8,
    state="disabled",
    command=lambda: copy_pub_key(),
)
copy_btn.grid(row=5, column=0, columnspan=2, sticky="w", pady=(0, 20))

#connect
tk.Label(
    setup_frame,
    text="2. carga la clave pública del peer y conecta",
    font=("Courier", 9),
    fg="gray",
    bg="#f5f5f0",
    anchor="w",
).grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 6))

path_var              = tk.StringVar()
port_var              = tk.StringVar()
other_person_port_var = tk.StringVar()
ip_var                = tk.StringVar()

_fields = [
    ("ruta clave pública del peer:", path_var),
    ("puerto local:",                port_var),
    ("puerto del peer:",             other_person_port_var),
    ("ip del peer:",                 ip_var),
]
for i, (label, var) in enumerate(_fields, start=7):
    tk.Label(
        setup_frame, text=label, anchor="e",
        font=("Courier", 10), bg="#f5f5f0",
    ).grid(row=i, column=0, sticky="e", padx=(0, 10), pady=5)
    tk.Entry(
        setup_frame, textvariable=var, width=34,
        font=("Courier", 10), relief="solid", bd=1,
    ).grid(row=i, column=1, sticky="w", pady=5)

setup_status_var = tk.StringVar(value="")
tk.Label(
    setup_frame, textvariable=setup_status_var,
    font=("Courier", 9), fg="gray", bg="#f5f5f0",
).grid(row=12, column=0, columnspan=2, pady=(4, 0))

connect_btn = tk.Button(
    setup_frame,
    text="conectar →",
    font=("Courier", 10),
    relief="solid",
    bd=1,
    padx=12,
    pady=4,
    state="disabled", 
    command=lambda: run(),
)
connect_btn.grid(row=11, column=0, columnspan=2, pady=16)

#chat window
chat_frame = tk.Frame(mainwindow, bg="#ffffff")

#header
header = tk.Frame(chat_frame, bg="#f0f0eb", padx=14, pady=10)
header.pack(fill="x")

peer_addr_var   = tk.StringVar(value="")
conn_status_var = tk.StringVar(value="conectando...")

tk.Label(
    header, text="Peer",
    font=("Courier", 12, "bold"), bg="#f0f0eb",
).pack(side="left")
tk.Label(
    header, textvariable=peer_addr_var,
    font=("Courier", 9), fg="#888", bg="#f0f0eb",
).pack(side="left", padx=(10, 0))
tk.Label(
    header, textvariable=conn_status_var,
    font=("Courier", 9), fg="#888", bg="#f0f0eb",
).pack(side="right")

tk.Frame(chat_frame, height=1, bg="#ddd").pack(fill="x")

#chat area
chat_container = tk.Frame(chat_frame, bg="#ffffff")
chat_container.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(chat_container)
scrollbar.pack(side="right", fill="y")

chat_text = tk.Text(
    chat_container,
    state="disabled",
    wrap="word",
    font=("Courier", 10),
    bg="#ffffff",
    relief="flat",
    bd=0,
    padx=14,
    pady=10,
    spacing1=3,
    spacing3=3,
    yscrollcommand=scrollbar.set,
)
chat_text.pack(side="left", fill="both", expand=True)
scrollbar.config(command=chat_text.yview)

chat_text.tag_configure(
    "recv",
    lmargin1=10, lmargin2=10, rmargin=160,
    background="#f0f0eb",
    spacing1=4, spacing3=1,
)
chat_text.tag_configure(
    "sent",
    lmargin1=160, lmargin2=160, rmargin=10,
    background="#dce8f5",
    justify="right",
    spacing1=4, spacing3=1,
)
chat_text.tag_configure(
    "meta_recv",
    lmargin1=10, lmargin2=10, rmargin=160,
    foreground="#aaa",
    font=("Courier", 8),
    spacing1=1, spacing3=6,
)
chat_text.tag_configure(
    "meta_sent",
    lmargin1=160, lmargin2=160, rmargin=10,
    foreground="#aaa",
    font=("Courier", 8),
    justify="right",
    spacing1=1, spacing3=6,
)
chat_text.tag_configure(
    "divider",
    justify="center",
    foreground="#aaa",
    font=("Courier", 8),
    spacing1=8, spacing3=8,
)

# public key
tk.Frame(chat_frame, height=1, bg="#ddd").pack(fill="x")

key_bar_var = tk.StringVar(value="")
tk.Label(
    chat_frame,
    textvariable=key_bar_var,
    font=("Courier", 7),
    fg="#aaa",
    bg="#fafaf8",
    anchor="w",
    padx=10,
    pady=3,
).pack(fill="x")

#input
tk.Frame(chat_frame, height=1, bg="#ddd").pack(fill="x")

input_frame = tk.Frame(chat_frame, bg="#ffffff", padx=10, pady=8)
input_frame.pack(fill="x")

input_text = tk.Text(
    input_frame,
    height=2,
    font=("Courier", 10),
    wrap="word",
    relief="solid",
    bd=1,
)
input_text.pack(side="left", fill="x", expand=True, padx=(0, 8))

send_btn = tk.Button(
    input_frame,
    text="enviar",
    font=("Courier", 9),
    relief="solid",
    bd=1,
    padx=10,
)
send_btn.pack(side="right", fill="y")

#logic
def generate_key() -> None:
    global _priv_key, _pub_pem

    _priv_key, pub = gen_dual_key()
    _pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    pub_key_display.configure(state="normal")
    pub_key_display.delete("1.0", "end")
    pub_key_display.insert("1.0", _pub_pem.decode("utf-8"))
    pub_key_display.configure(state="disabled")

    copy_btn.configure(state="normal")
    connect_btn.configure(state="normal")
    setup_status_var.set("clave generada — compártela con el peer antes de conectar")


def copy_pub_key() -> None:
    mainwindow.clipboard_clear()
    mainwindow.clipboard_append(_pub_pem.decode("utf-8"))
    setup_status_var.set("clave copiada al portapapeles")


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M")


def append_message(text: str, direction: str) -> None:
    chat_text.configure(state="normal")
    if direction == "recv":
        chat_text.insert("end", f" {text}\n", "recv")
        chat_text.insert("end", f" [enc] {_timestamp()}\n", "meta_recv")
    else:
        chat_text.insert("end", f"{text} \n", "sent")
        chat_text.insert("end", f"{_timestamp()} [enc] \n", "meta_sent")
    chat_text.configure(state="disabled")
    chat_text.see("end")


def _poll_messages() -> None:
    try:
        while True:
            msg = msg_queue.get_nowait()
            append_message(msg, "recv")
    except queue.Empty:
        pass
    mainwindow.after(100, _poll_messages)


def _poll_connection(event: threading.Event) -> None:
    if event.is_set():
        conn_status_var.set("● conectado")
        chat_text.configure(state="normal")
        chat_text.insert("end", "── sesión iniciada — cifrado E2E activo ──\n", "divider")
        chat_text.configure(state="disabled")
        chat_text.see("end")
    else:
        mainwindow.after(1000, _poll_connection, event)


def send_message(event=None) -> str:
    if event and (event.state & 0x1):
        return

    msg = input_text.get("1.0", "end-1c").strip()
    if not msg:
        return "break"

    input_text.delete("1.0", "end")
    append_message(msg, "sent")
    send_queue.put(msg)     # FIX: deposita en la cola para que el thread cliente transmita

    return "break"


def setup_key(path: str):
    with open(path, "r") as f:
        data = f.read()
    return serialization.load_pem_public_key(data.encode("utf-8"))


def switch_to_chat(sendto_ip: str, sendto_port: int) -> None:
    setup_frame.pack_forget()
    peer_addr_var.set(f"  {sendto_ip}:{sendto_port}")
    chat_frame.pack(fill="both", expand=True)
    mainwindow.after(100, _poll_messages)


def run() -> None:
    global _priv_key, _pub_pem

    if _priv_key is None:
        setup_status_var.set("genera tu clave antes de conectar")
        return

    path_value  = path_var.get().strip()
    port_value  = int(port_var.get().strip())
    sendto_ip   = ip_var.get().strip()
    sendto_port = int(other_person_port_var.get().strip())

    setup_status_var.set("conectando...")
    mainwindow.update_idletasks()

    peer_pub_key = setup_key(path_value)

    listener_thread = threading.Thread(
        target=__socket__,
        args=(port_value, _priv_key, msg_queue),
        daemon=True,
    )
    listener_thread.start()

    event = threading.Event()
    client_thread = threading.Thread(
        target=__socket_client__,
        args=(sendto_ip, sendto_port, peer_pub_key, event, send_queue),
        daemon=True,
    )
    client_thread.start()

    pub_pem_str = _pub_pem.decode("utf-8").replace("\n", " ").strip()
    key_bar_var.set("mi pub: " + pub_pem_str[:110] + "...")

    switch_to_chat(sendto_ip, sendto_port)
    mainwindow.after(1000, _poll_connection, event)


#input bindings
send_btn.configure(command=send_message)
input_text.bind("<Return>", send_message)
#loop
mainwindow.mainloop()
def main():
    run()

if __name__ == "__main__":
    main()