""" Script for Tkinter GUI chat client. """
import tkinter
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def generateKeys():
    e = d = N = 0

    p = 5099
    q = 4759

    N = p * q 
    phiN = (p - 1) * (q - 1)

    while True:
        e = 1013
        if (isCoPrime(e, phiN)):
            break

    d = modularInv(e, phiN)

    return e, d, N

def isCoPrime(p, q):
    return gcd(p, q) == 1

def gcd(p, q):
    while q:
        p, q = q, p % q
    return p

def egcd(a, b):
    s = 0; old_s = 1
    t = 1; old_t = 0
    r = b; old_r = a

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    # return gcd, x, y
    return old_r, old_s, old_t

def modularInv(a, b):
    gcd, x, y = egcd(a, b)

    if x < 0:
        x += b
    return x

def decrypt(d, N, cipher):
    msg = ""
    parts = cipher.split()
    for part in parts:
        if part:
            c = int(part)
            msg += chr(pow(c, d, N))
    return msg

def encrypt(e, N, msg):
    cipher = ""
    for c in msg:
        m = ord(c)
        cipher += str(pow(m, e, N)) + " "

    return cipher

e, d, N = generateKeys()

def receive():
    """ Handles receiving of messages. """
    while True:
        try:
            #msg = sock.recv(BUFSIZ).decode("utf8")
            msg = (sock.recv(1024)).decode()
            dec = decrypt(d, N, msg)
            print(dec)
            msg_list.insert(tkinter.END, dec)
        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):
    """ Handles sending of messages. """
    msg = my_msg.get()
    
    enc = encrypt(e, N, msg)
    print(enc)
    
    my_msg.set("")  # Clears input field.
    sock.send(enc.encode())
    if msg == "#quit":
        sock.close()
        top.quit()

def on_closing(event=None):
    """ This function is to be called when the window is closed. """
    my_msg.set("#quit")
    send()

top = tkinter.Tk()
top.title("Simple Cypher Client")
messages_frame = tkinter.Frame(top)

my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=70, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()

messages_frame.pack()

button_label = tkinter.Label(top, text="Enter Message:")
button_label.pack()
entry_field = tkinter.Entry(top, textvariable=my_msg, foreground="Red")
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()


quit_button = tkinter.Button(top, text="Quit", command=on_closing)
quit_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)



HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.
