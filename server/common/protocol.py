from .utils import Bet
from typing import List
from common.constants import SOCKET_MESSAGE_LENGTH_BYTES, ENCODING_FORMAT, LINE_TERMINATOR, MAX_MESSAGE_LENGTH
import struct
from common.constants import SOCKET_MESSAGE_LENGTH_BYTES, ENCODING_FORMAT, LINE_TERMINATOR, MAX_MESSAGE_LENGTH
import struct

def receive_message(client_sock) -> str:
def receive_message(client_sock) -> str:
    """
    Reads the message ID from the client socket
    """
    length = int.from_bytes(client_sock.recv(SOCKET_MESSAGE_LENGTH_BYTES), byteorder='big')
    
    length = int.from_bytes(client_sock.recv(SOCKET_MESSAGE_LENGTH_BYTES), byteorder='big')
    
    if length == 0:
        return ""
    
        return ""
    
    data = b""

    while len(data) < length:
        chunk = client_sock.recv(length - len(data))
        if not chunk:
            # Connection closed before we received the entire message
            return "", True
            return "", True
        data += chunk
    return data.decode(ENCODING_FORMAT).strip()

def send_message(client_sock, data):
    """
    Responds to a client by sending the length of the message followed by the message itself.
    """
    message = f"{data}{LINE_TERMINATOR}".encode(ENCODING_FORMAT)
    length = len(message)

    if length > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Message too long: length is {length} bytes, but max is {MAX_MESSAGE_LENGTH}")

  # Convert length to a 2-byte integer in Big Endian format
    length_bytes = struct.pack('!H', length)
    client_sock.send(length_bytes)
    client_sock.send(message)