import socket
import logging
import signal
import sys

from common.protocol import receive_message, send_message, receive_message_chunks
from common.utils import store_bets

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._active_connections = []
        
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

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
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
            count_chunks = receive_message_chunks(client_sock)
            error_processing_chunks = False
            # logging.info(f'chunks_recibidos | result: success | cantidad: {count_chunks}')
            cantidad_apuestas = 0
            for i in range(count_chunks):
                bets,hasError = receive_message(client_sock,i,count_chunks)

                if hasError:
                    error_processing_chunks = True
                                    
                cantidad_apuestas += len(bets)
                for bet in bets:
                    store_bets([bet])

                # if len(bets) > 0:
                    # logging.info(f'apuestas_procesadas | result: success | cantidad: {len(bets)}')

            # if error_processing_chunks:
            #     # logging.error(
            #     #     f'apuesta_recibida | result: fail | cantidad: {cantidad_apuestas}')
            #     send_message(client_sock, "Error")
            # else:
            #     # logging.info(
            #     #     f'apuesta_recibida | result: success | cantidad: {cantidad_apuestas}')
            #     send_message(client_sock, "Ok")
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
            send_message(client_sock, "Error")
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
