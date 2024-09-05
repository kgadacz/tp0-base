from .utils import Bet
from typing import List
from common.constants import SOCKET_MESSAGE_LENGTH_BYTES, ENCODING_FORMAT, LINE_TERMINATOR

def receive_message(client_sock) -> str:
    """
    Reads the message ID from the client socket
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
    message = f"{data}{LINE_TERMINATOR}".encode(ENCODING_FORMAT)
    client_sock.send(message)
