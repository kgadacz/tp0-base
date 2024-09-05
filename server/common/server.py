import socket
import logging
import signal
import sys

from common.protocol import receive_message, send_message
from common.utils import store_bets
from common.bet_parser import parse_bets
from common.constants import ERROR_PROCESSING_CHUNKS_RESPONSE, OK_RESPONSE,ERROR_RESPONSE

class Server:
    def __init__(self, port, listen_backlog, amount_of_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._active_connections = []
        self._amount_of_clients = amount_of_clients
        
        signal.signal(signal.SIGINT, self.__handle_signal)
        signal.signal(signal.SIGTERM, self.__handle_signal)


    def __handle_signal(self, signum, frame):
        logging.info(f"action: signal {signum} | result: in_progress")
        
        for client_sock in self._active_connections:
            try:
                logging.debug("action: close client socket | result: in_progress")
                client_sock.close()
                logging.debug("action: close client socket | result: success")
            except OSError as e:
                logging.error(f"action: close client socket | result: fail | error: {e}")
        
        
        logging.debug("action: close server socket | result: in_progress")
        self._server_socket.close()
        logging.debug("action: close server socket | result: success")
        
        logging.info(f"action: signal {signum} | result: success")
        sys.exit(0)


    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        while True:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        self._active_connections.append(client_sock)
       
        try:
            count_chunks = int(receive_message(client_sock))
            error_processing_chunks = False
            logging.debug(f'chunks_recibidos | result: success | cantidad: {count_chunks}')
            cantidad_apuestas = 0
            for _ in range(count_chunks):
                bets,hasError = parse_bets(receive_message(client_sock))
                if hasError:
                    error_processing_chunks = True
                    send_message(client_sock, ERROR_RESPONSE)
                else:
                    cantidad_apuestas += len(bets)
                    send_message(client_sock, OK_RESPONSE)
                    for bet in bets:
                        store_bets([bet])
            if error_processing_chunks:
                logging.error(f'apuestas_recibidas | result: fail | cantidad: {cantidad_apuestas}')
                send_message(client_sock, ERROR_PROCESSING_CHUNKS_RESPONSE)
            else:
                logging.info(f'apuestas_recibidas | result: success | cantidad: {cantidad_apuestas}')
                send_message(client_sock, OK_RESPONSE)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
            send_message(client_sock, ERROR_PROCESSING_CHUNKS_RESPONSE)
        finally:
            client_sock.close()
            self._active_connections.remove(client_sock)

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
