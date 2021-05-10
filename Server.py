""" Script for TCP chat server - relays messages to all clients """
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

clients = {}
addresses = {}

HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(ADDR)

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SOCK.accept()
        print("%s:%s has connected." % client_address)
        greet = "Greetings from the Chat Room!"
        enc = encrypt(e, N, greet)
        client.send(enc.encode())
        inst = "Please type your name and press enter!"
        enc2 = encrypt(e, N, inst)
        client.send(enc2.encode())
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(conn, addr):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = conn.recv(1024).decode()
    dec = decrypt(d, N, name)
    name = dec
    welcome = '\nWelcome %s! If you ever want to quit, type #quit to exit.' % name
    enc = encrypt(e, N, welcome)
    conn.send(enc.encode())
    clients[conn] = name
    quuit = "#quit"
    while True:
        msg = conn.recv(1024)
        dec2 = decrypt(d, N, msg)
        msg = dec2
        if msg != bytes("#quit", "utf8"):
            broadcast(msg, name + ": ")
        else:
            encQuit = encrypt(e, N, quuit)
            quuit = encQuit
            conn.send(quuit.encode())
            conn.close()
            del clients[conn]
            broadcast(bytes("\n%s has left the chat." % name, "utf8"))
            break

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients:
        enc = encrypt(e, N, msg)
        msg = enc
        sock.send(msg.encode())

if __name__ == "__main__":
    SOCK.listen(5)  # Listens for 5 connections at max.
    print("Chat Server has Started !!")
    print("Waiting for connections...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SOCK.close()
