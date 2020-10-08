import socket
import sys
import _thread
import packet
import udt
from timer import Timer
import time

# Some already defined parameters
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05  # (In seconds)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4


# You can use some shared resources over the two threads
base = 0
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)

# Need to have two threads: one for sending and another for receiving ACKs

# Generate random payload of any length
def generate_payload(length=10):
    global base
    initial_byte = PACKET_SIZE * base
    result_str = ''.join(bio[i] for i in range(initial_byte, initial_byte + length))
    return result_str

def total_seq(length):
    count = 0
    while True:
        num, remainder = divmod(length, PACKET_SIZE)
        if remainder:
            break
        else:
            count += 1
    return num + 1

# Send using Stop_n_wait protocol
def send_snw(sock):
    global base
    global mutex
    global timer
    last_seq = total_seq(len(bio))
    _thread.start_new_thread(receive_snw, (sock, ))
    while (base < last_seq):
        mutex.acquire()
        if base == last_seq - 1:
            data = generate_payload(len(bio) - (PACKET_SIZE * base)).encode()
        elif base == last_seq:
            print('Transfer complete... Sending FIN\n')
            data = "END".encode()
        else:
            data = generate_payload(PACKET_SIZE).encode()
        pkt = packet.make(base, data)
        print('Sending SEQ #', base, "\n")
        udt.send(pkt, sock, RECEIVER_ADDR)

        if not timer.running():
            timer.start()

        while timer.running() and not timer.timeout():
            mutex.release()
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        if timer.timeout():
            print('===================TIMEOUT====================')
            timer.stop()
        mutex.release()

    print('Transfer complete... Sending FIN\n')
    data = "END".encode()
    pkt = packet.make(base, data)
    udt.send(pkt, sock, RECEIVER_ADDR)

# Send using GBN protocol
def send_gbn(sock):
    return


# Receive thread for stop-n-wait
def receive_snw(sock):
    global base
    global mutex
    global timer
    while base < total_seq(len(bio)):
        pkt, senderaddr = udt.recv(sock)
        ack, data = packet.extract(pkt)
        print('Received ACK #', ack, "\n")
        if ack >= base:
            mutex.acquire()
            base += 1
            timer.stop
            mutex.release()

# Receive thread for GBN
def receive_gbn(sock):
    # Fill here to handle acks
    return


# Main function
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Expected filename as command line argument')
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    filename = sys.argv[1]
    file = open(filename, 'r')
    bio = file.read()

    send_snw(sock)
    sock.close()
