from .utils import Bet
from typing import List
from common.constants import SOCKET_MESSAGE_LENGTH_BYTES, ENCODING_FORMAT, LINE_TERMINATOR, MAX_MESSAGE_LENGTH
import struct

def receive_message(client_sock) -> str:
    """
    Reads the message from the client socket. Handles short reads.
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
    Sends a message to the client by sending the length of the message followed by the message itself.
    Handles short writes.
    """
    message = f"{data}{LINE_TERMINATOR}".encode(ENCODING_FORMAT)
    length = len(message)

    if length > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Message too long: length is {length} bytes, but max is {MAX_MESSAGE_LENGTH}")

    # Convert length to a 2-byte integer in Big Endian format
    length_bytes = struct.pack('!H', length)
    
    # Ensure all bytes are sent
    total_sent = 0
    while total_sent < len(length_bytes):
        sent = client_sock.send(length_bytes[total_sent:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        total_sent += sent
    
    total_sent = 0
    while total_sent < len(message):
        sent = client_sock.send(message[total_sent:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        total_sent += sent