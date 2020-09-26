import socket
import sys
# import _thread
import time
import string
import packet
import udt
import random
from timer import Timer

# Some already defined parameters
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05 # (In seconds)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4
TEMP = 0


# You can use some shared resources over the two threads
# base = 0
# mutex = _thread.allocate_lock()
# timer = Timer(TIMEOUT_INTERVAL)

# Need to have two threads: one for sending and another for receiving ACKs

# Generate random payload of any length
def generate_payload(length=10):
    global TEMP
    result_str = ''.join(bio[TEMP] for TEMP in range(length))
    TEMP = TEMP + length
    return result_str


# Send using Stop_n_wait protocol
def send_snw(sock):
    # Fill out the code here

    seq = 0
    while(seq < 20):
        data = generate_payload(PACKET_SIZE).encode()
        pkt = packet.make(seq, data)
        print("Sending seq# ", seq, "\n")
        udt.send(pkt, sock, RECEIVER_ADDR)
        seq = seq+1
        time.sleep(TIMEOUT_INTERVAL)
    pkt = packet.make(seq, "END".encode())
    udt.send(pkt, sock, RECEIVER_ADDR)

# Send using GBN protocol
def send_gbn(sock):

    return

# Receive thread for stop-n-wait
def receive_snw(sock, pkt):
    # Fill here to handle acks
    return

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

    print('FIRST: ' + generate_payload(PACKET_SIZE))
    print('SECOND: ' + generate_payload(PACKET_SIZE))

    count = 0
    while True:
        num, remainder = divmod(len(bio), PACKET_SIZE)
        if remainder:
            break
        else:
            count += 1
    print(len(bio))
    print(num)

   # send_snw(sock)
    sock.close()
