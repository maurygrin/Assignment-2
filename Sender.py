# Team 16
# Assignment 02: Reliable Data Transfer
# October 09, 2020
# CS5313 - Computer Networks

import socket
import _thread
import packet
import udt
import time
from timer import Timer

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

# Generate payload for snw protocol using the given length and the initial byte of the packet
def generate_payload_snw(length):
    global base
    initial_byte = PACKET_SIZE * base
    result_str = ''.join(bio[i] for i in range(initial_byte, initial_byte + length))
    return result_str


# Generate payload for gbn protocol using the given length and the initial byte of the packet
def generate_payload_gbn(length, SEQN):
    initial_byte = PACKET_SIZE * SEQN
    result_str = ''.join(bio[i] for i in range(initial_byte, initial_byte + length))
    return result_str


# Calculates how many SEQ are going to be sent by using the length of the file
def total_SEQ(length):
    count = 0

    # Calculates how many times length can be divided by PACKET_SIZE
    while True:
        num, remainder = divmod(length, PACKET_SIZE)

        if remainder:
            break

        else:
            count += 1

    return num


# Send using Stop_n_wait protocol
def send_snw(sock):
    global base
    global mutex
    global timer

    # Last SEQ to be sent
    last_SEQ = total_SEQ(len(bio))

    # Starts the receiving thread
    _thread.start_new_thread(receive_snw, (sock,))

    # Auxiliary variable for FIN
    rep = 0

    # Sends packets until is done
    while base <= last_SEQ + 1:
        mutex.acquire()

        # Sends FIN 6 times if FIN ACK was not received. Ensures that receiver receives FIN packet
        if rep == 6:
            break

        # Last part of the text is going to be sent
        if base == last_SEQ - 1:
            data = generate_payload_snw(len(bio) - (PACKET_SIZE * base)).encode()

        # The text was sent. Time to send FIN to end the connection
        elif base == last_SEQ:
            print('Transfer complete... Sending FIN', "\n")
            data = "END".encode()
            rep += 1

        # FIN has been received... Ending connection
        elif base == last_SEQ + 1:
            break

        # Regular packet is going to be sent
        else:
            data = generate_payload_snw(PACKET_SIZE).encode()

        pkt = packet.make(base, data)
        print('Sending SEQ #', base, "\n")
        udt.send(pkt, sock, RECEIVER_ADDR)

        # Check if timer is running. Start if is not running
        if not timer.running():
            timer.start()

        # Waits 0.05 seconds and checks for the timer
        while timer.running() and not timer.timeout():
            mutex.release()
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        # Waiting time exceeded... Time out
        if timer.timeout():
            print('Time out', "\n")
            timer.stop()

        mutex.release()

    print('FIN has been received... Ending connection')


# Send using GBN protocol
def send_gbn(sock):
    global base
    global mutex
    global timer

    # Last SEQ to be sent
    last_SEQ = total_SEQ(len(bio))

    # Current SEQ
    SEQN = 0

    # Starts the receiving thread
    _thread.start_new_thread(receive_gbn, (sock,))

    # Auxiliary variable for FIN
    rep = 0

    # Sends packets until is done
    while base <= last_SEQ + 1:
        mutex.acquire()

        # Check the window size and remaining packets
        window = min(WINDOW_SIZE, last_SEQ - base)

        # Send packets until it reach the limit of the window size
        while SEQN <= base + (window - 1):

            # Last part of the text is going to be sent
            if SEQN == last_SEQ - 1:
                data = generate_payload_gbn(len(bio) - (PACKET_SIZE * SEQN), SEQN).encode()

            # Last packet was sent
            elif SEQN == last_SEQ:
                break

            # Regular packet is going to be sent
            else:
                data = generate_payload_gbn(PACKET_SIZE, SEQN).encode()

            pkt = packet.make(SEQN, data)
            print('Sending SEQ #', SEQN, "\n")
            udt.send(pkt, sock, RECEIVER_ADDR)

            SEQN += 1

        # Sends FIN 6 times if FIN ACK was not received. Ensures that receiver receives FIN packet
        if rep == 6:
            break

        # The text was sent. Time to send FIN to end the connection
        if base == last_SEQ:
            print('Transfer complete... Sending FIN', "\n")
            data = "END".encode()
            pkt = packet.make(SEQN, data)
            print('Sending SEQ #', SEQN, "\n")
            udt.send(pkt, sock, RECEIVER_ADDR)
            rep += 1

        # FIN has been received... Ending connection
        elif base == last_SEQ + 1:
            break

        # Check if timer is running. Start if is not running
        if not timer.running():
            timer.start()

        # Waits 0.05 seconds and checks for the timer
        while timer.running() and not timer.timeout():
            mutex.release()
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        # Waiting time exceeded... Time out
        if timer.timeout():
            print('Time out', "\n")
            timer.stop()
            SEQN = base

        mutex.release()

    print('FIN has been received... Ending connection')


# Receive thread for stop-n-wait
def receive_snw(sock):
    global base
    global mutex
    global timer

    # Receives ACK until the last one was received
    while base <= total_SEQ(len(bio)):
        pkt, senderaddr = udt.recv(sock)
        ACK, data = packet.extract(pkt)
        print('Received ACK #', ACK, "\n")

        # Updates base if ACK is equal or greater than base
        if ACK >= base:
            mutex.acquire()
            base += 1
            timer.stop
            mutex.release()


# Receive thread for GBN
def receive_gbn(sock):
    global base
    global mutex
    global timer

    # Receives ACK until the last one was received
    while base <= total_SEQ(len(bio)):
        pkt, senderaddr = udt.recv(sock)
        ACK, data = packet.extract(pkt)
        print('Received ACK #', ACK, "\n")

        # Updates base if ACK is equal or greater than base(Slide window)
        if ACK >= base and ACK != total_SEQ(len(bio)):
            mutex.acquire()
            base = ACK + 1
            timer.stop
            mutex.release()

        # The packets being sent are not expected. Updates base with the expected SEQ
        else:
            mutex.acquire()
            base = ACK
            timer.stop
            mutex.release()


# Main function
if __name__ == '__main__':

    # Select a protocol
    print('Enter protocol(1: SnW - 2: GBn): ')
    protocol = input()

    # Check the user input
    if protocol is not '1' and protocol is not '2':
        print('Invalid protocol... Terminating')
        exit()

    # Enter file name
    print('Enter filename: ')
    filename = input()

    # Check the user input
    if len(filename) != 1 and '.txt' not in filename:
        print('Invalid input file... Terminating')
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    file = open(filename, 'r')
    bio = file.read()

    # Starts Stop-and-Wait sender
    if protocol is '1':
        send_snw(sock)

    # Starts Go-Back-N sender
    elif protocol is '2':
        send_gbn(sock)

    sock.close()
