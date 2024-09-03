import logging

from .utils import Bet

def receive_message(client_sock) -> Bet:
    """
    Reads data from a specific client socket
    """
    
    len = int.from_bytes(client_sock.recv(2), byteorder='big')
    msg = client_sock.recv(len).decode('utf-8').strip()
    addr = client_sock.getpeername()
    logging.info(
        f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')

    return Bet(*msg.split(','))


def send_message(client_sock, data):
    """
    Responds to a client
    """
    client_sock.send("{}\n".format(data).encode('utf-8'))