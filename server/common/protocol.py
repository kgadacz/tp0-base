import logging

from .utils import Bet
from typing import List
from common.constants import SOCKET_MESSAGE_LENGTH_BYTES, ENCODING_FORMAT, LINE_TERMINATOR, MAX_MESSAGE_LENGTH
import struct

def receive_message(client_sock, nro_chunk, total_chunks) -> List[str]:
    """
    Reads data from a specific client socket
    """
    length = int.from_bytes(client_sock.recv(SOCKET_MESSAGE_LENGTH_BYTES), byteorder='big')
    
    if length == 0:
        return ""
    
    data = b""

    while len(data) < length:
        chunk = client_sock.recv(length - len(data))
        if not chunk:
            # Connection closed before we received the entire message
            return "", True
        data += chunk
    return data.decode(ENCODING_FORMAT).strip()


def send_message(client_sock, data):
    """
    Responds to a client
    """
    client_sock.send("{}\n".format(data).encode('utf-8'))