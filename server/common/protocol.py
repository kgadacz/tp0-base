import logging
import struct
from .utils import Bet
from typing import List

def receive_message(client_sock, nro_chunk, total_chunks) -> List[Bet]:
    """
    Reads data from a specific client socket and returns a list of Bet objects.
    Each Bet object is created from a comma-separated string, and multiple Bet objects
    are separated by semicolons.
    """

    hasError = False

    # Read the length of the incoming message
    length = int.from_bytes(client_sock.recv(2), byteorder='big')

    if length == 0:
        return [], True

    # Read the message based on the length, but ensure all data is received
    data = b""
    while len(data) < length:
        chunk = client_sock.recv(length - len(data))
        if not chunk:
            # Connection closed before we received the entire message
            return [], True
        data += chunk
    
    try:
        msg = data.decode('utf-8').strip()
        logging.info(f'chunk {nro_chunk}/{total_chunks}: {msg}')
    except UnicodeDecodeError as e:
        return [], True

    # Split the message by semicolon to handle multiple Bet records
    bet_records = msg.split(';')

    # Create a list of Bet objects from the split records
    bets = []

    for record in bet_records:
        fields = record.split(',')

        if len(fields) != 6:
            hasError = True
            continue  # Skip this record and proceed with the next

        try:
            # Create a Bet object
            bet = Bet(*fields)
            bets.append(bet)
        except TypeError as e:
            hasError = True
        except Exception as e:
            hasError = True

    return bets, hasError

def receive_message_chunks(client_sock) -> int:
    """
    Reads data from a specific client socket and returns the number of chunks
    """
    # Define the buffer size (4 bytes for a 32-bit integer)
    buffer_size = 4

    # Receive the data
    data = client_sock.recv(buffer_size)

    # Ensure we received the expected amount of data
    if len(data) < buffer_size:
        raise ValueError("Received incomplete data from the client")

    # Unpack the data from big-endian byte order to an integer
    count_chunks = struct.unpack('!I', data)[0]

    return count_chunks

def send_message(client_sock, data):
    """
    Responds to a client
    """
    client_sock.send("{}\n".format(data).encode('utf-8'))
