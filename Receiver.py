# receiver.py - The receiver in the reliable data transfer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8080)


# Receive packets from the sender w/ GBN protocol
def receive_gbn(sock):
    # Fill here
    return


# Receive packets from the sender w/ SR protocol
def receive_sr(sock, windowsize):
    # Fill here
    return


# Receive packets from the sender w/ Stop-n-wait protocol
def receive_snw(sock):
    endStr = ''
    expectedPacket = 0
    while endStr != 'END':
        pkt, senderaddr = udt.recv(sock)
        seq, data = packet.extract(pkt)
        endStr = data.decode()
        print("From: ", senderaddr, ", Seq# ", seq, endStr)
        if expectedPacket != seq:
            print('This packet was not expected. Sending ACK %d' % (expectedPacket - 1))
            pkt = packet.make(expectedPacket - 1)
            udt.send(pkt, sock, senderaddr)
        else:
            print('Successfully received. Sending ACK %d' % expectedPacket)
            pkt = packet.make(expectedPacket)
            udt.send(pkt, sock, senderaddr)
            expectedPacket += 1
            file.write(data)


# Main function
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Expected filename as command line argument')
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    filename = sys.argv[1]
    file = open(filename, 'w')
    receive_snw(sock)

    # Close the socket
    sock.close()
