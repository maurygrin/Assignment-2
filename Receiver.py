# Team 16
# Assignment 02: Reliable Data Transfer
# October 09, 2020
# CS5313 - Computer Networks

import packet
import socket
import udt

RECEIVER_ADDR = ('localhost', 8080)

# Receive packets from the sender w/ GBN protocol
def receive_gbn(sock):
    endStr = ''
    expectedPacket = 0

    # While FIN packet has not been received
    while endStr != 'END':
        pkt, senderaddr = udt.recv(sock)
        SEQ, data = packet.extract(pkt)
        endStr = data.decode()
        print("From: ", senderaddr, ", SEQ# ", SEQ)

        # The received packet was not expected. Send ACK with the correct SEQ number
        if expectedPacket != SEQ:
            print('This packet was not expected. Sending ACK %d' % expectedPacket, "\n")
            pkt = packet.make(expectedPacket)
            udt.send(pkt, sock, senderaddr)

        # This packet was expected. Send ACK with the next SEQ number expected
        else:
            print('Successfully received SEQ #%d. Sending ACK #%d' % (SEQ, expectedPacket), "\n")
            pkt = packet.make(expectedPacket)
            udt.send(pkt, sock, senderaddr)
            expectedPacket += 1

            # Makes sure that the FIN packet is not added to the text
            if endStr != 'END':
                file.write(data.decode())

    print('FIN has been ACK... Ending connection')

# Receive packets from the sender w/ SR protocol
def receive_sr(sock, windowsize):
    # Fill here
    return


# Receive packets from the sender w/ Stop-n-wait protocol
def receive_snw(sock):
    endStr = ''
    expectedPacket = 0

    # While FIN packet has not been received
    while endStr != 'END':
        pkt, senderaddr = udt.recv(sock)
        SEQ, data = packet.extract(pkt)
        endStr = data.decode()
        print("From: ", senderaddr, ", SEQ# ", SEQ)

        # The received packet was not expected. Send ACK with the correct SEQ number
        if expectedPacket != SEQ:
            print('This packet was not expected. Sending ACK %d' % expectedPacket, "\n")
            pkt = packet.make(expectedPacket)
            udt.send(pkt, sock, senderaddr)

        # This packet was expected. Send ACK with the next SEQ number expected
        else:
            print('Successfully received SEQ #%d. Sending ACK #%d' % (SEQ, expectedPacket), "\n")
            pkt = packet.make(expectedPacket)
            udt.send(pkt, sock, senderaddr)
            expectedPacket += 1

            # Makes sure that the FIN packet is not added to the text
            if endStr != 'END':
                file.write(data.decode())

    print('FIN has been ACK... Ending connection')

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
    sock.bind(RECEIVER_ADDR)

    file = open(filename, 'w')

    # Starts Stop-and-Wait receiver
    if protocol is '1':
        receive_snw(sock)

    # Starts Go-Back-N receiver
    elif protocol is '2':
        receive_gbn(sock)

    # Close the socket
    sock.close()
