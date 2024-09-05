import socket
import logging
import signal
import sys
import multiprocessing
from common.protocol import send_message, receive_message
from common.utils import store_bets, load_bets, has_won
from common.bet_parser import parse_bets
from common.constants import (
    BET_TYPE_MESSAGE, WINNER_TYPE_MESSAGE,
    OK_RESPONSE, ERROR_RESPONSE, REFUSED_RESPONSE
)

class Server:
    def __init__(self, port, listen_backlog, amount_of_clients):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._active_connections = []
        self.processes = []
        self._amount_of_clients = amount_of_clients
        # Create a manager for shared data and lock
        manager = multiprocessing.Manager()
        self._clients_bets_finished = manager.Value('i', 0)
        self._clients_bets_finished_lock = manager.Lock()
        self._store_bets_lock = manager.Lock()
        
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

        for process in self.processes:
            process.join()
        logging.debug(f'action: join process | result: success')

        sys.exit(0)

    def run(self):
        """
        Server loop

        Accepts new connections and spawns a process to handle each client.
        """
        while True:
            client_sock = self.__accept_new_connection()
            client_proccess = multiprocessing.Process(
                target=self.__handle_client_connection,
                args=(client_sock,))
            client_proccess.start()
            self.processes.append(client_proccess)

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
            
            # Critical section: store bets (synchronized with lock)
            logging.info("pido el lock para store_bets")
            with self._store_bets_lock:
                store_bets([bet for bet in bets])
            logging.info("libero el lock para store_bets")
        logging.info("pido el lock para incrementar el contador de apuestas")
        with self._clients_bets_finished_lock:
            self._clients_bets_finished.value += 1
        logging.info("libero el lock para incrementar el contador de apuestas")
        if error_processing_chunks:
            logging.error(f'apuestas_recibidas | result: fail | cantidad: {cantidad_apuestas}')
        else:
            logging.info(f'apuestas_recibidas | result: success | cantidad: {cantidad_apuestas}')

    def __handle_ask_client_winner(self, client_sock):
        id = int(receive_message(client_sock))
        # Check if all clients have finished placing bets (synchronized with lock)
        with self._clients_bets_finished_lock:
            logging.debug("Usando lock para sorteo en el cliente {}".format(id))
            if self._clients_bets_finished.value < self._amount_of_clients:
                logging.error("action: sorteo | result: fail")
                send_message(client_sock, REFUSED_RESPONSE)
            else:
                logging.info("action: sorteo | result: success")
                amount_winners = self.__handle_get_amount_winners(id)
                send_message(client_sock, str(amount_winners))
        logging.debug("Libero el lock para sorteo en el cliente {}".format(id))

    def __handle_get_amount_winners(self, id):
        winners = 0
        
        for bet in load_bets():
            if has_won(bet) and bet.agency == id:
                winners += 1
        return winners

    def __handle_client_connection(self, client_sock):
        """
        Handle communication with a client in a separate process.
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
        Accept new connections.

        Blocks until a connection to a client is made.
        """
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
