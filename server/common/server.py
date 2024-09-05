import socket
import logging
import signal
import sys

from common.protocol import send_message, receive_message
from common.utils import store_bets, load_bets, has_won
from common.bet_parser import parse_bets
from common.constants import (
    AMOUNT_OF_CLIENTS,
    BET_TYPE_MESSAGE, WINNER_TYPE_MESSAGE,
    OK_RESPONSE, ERROR_RESPONSE, REFUSED_RESPONSE
)

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._active_connections = []
        self._clients_bets_finished = 0
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

        Server that accepts new connections and establishes a
        communication with a client. After the communication
        finishes, the server starts to accept new connections again.
        """

        while True:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def __handle_client_bets(self, client_sock):
        count_chunks = int(receive_message(client_sock))
        error_processing_chunks = False
        logging.debug(f'chunks_recibidos | result: success | cantidad: {count_chunks}')
        cantidad_apuestas = 0

        for i in range(count_chunks):
            data = receive_message(client_sock)
            bets, hasError = parse_bets(data)
            send_message(client_sock, OK_RESPONSE)

            if hasError:
                error_processing_chunks = True
                                
            cantidad_apuestas += len(bets)
            for bet in bets:
                store_bets([bet])

        self._clients_bets_finished += 1
        if error_processing_chunks:
            logging.error(f'apuestas_recibidas | result: fail | cantidad: {cantidad_apuestas}')
        else:
            logging.info(f'apuestas_recibidas | result: success | cantidad: {cantidad_apuestas}')

    def __handle_ask_client_winner(self, client_sock):
        id = int(receive_message(client_sock))

        if self._clients_bets_finished < AMOUNT_OF_CLIENTS:
            logging.error("action: sorteo | result: fail")
            send_message(client_sock, REFUSED_RESPONSE)
        else:
            logging.info("action: sorteo | result: success")
            amount_winners = self.__handle_get_amount_winners(id)
            send_message(client_sock, str(amount_winners))

    def __handle_get_amount_winners(self, id):
        winners = 0
        for bet in load_bets():
            if has_won(bet) and bet.agency == id:
                winners += 1
        return winners

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed.
        """
        self._active_connections.append(client_sock)

        try:
            type_message = receive_message(client_sock)

            if type_message == BET_TYPE_MESSAGE:
                self.__handle_client_bets(client_sock)
            elif type_message == WINNER_TYPE_MESSAGE:
                self.__handle_ask_client_winner(client_sock)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            send_message(client_sock, ERROR_RESPONSE)
        finally:
            client_sock.close()
            self._active_connections.remove(client_sock)

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then the connection is printed and returned.
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
