package common

import (
	"net"
	"os"
	"os/signal"
	"syscall"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/domain"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/transport"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type Client struct {
	config     ClientConfig
	data 	   domain.ClientData
	conn       net.Conn
	signalChan chan os.Signal
	closeChan  chan bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, data domain.ClientData) *Client {
	client := &Client{
		config:     config,
		data:       data,
		signalChan: make(chan os.Signal, 1),
		closeChan:  make(chan bool),
	}

	// Notify the client when SIGTERM or SIGINT is received
	signal.Notify(client.signalChan, syscall.SIGTERM, syscall.SIGINT)

	// Start a goroutine to handle these signals
	go client.handleSignals()

	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {

	// Create the connection to the server
	c.createClientSocket()
	
	protocol := transport.NewProtocol(c.conn)

	err := protocol.SendMessage(c.data)

	if err == nil {
		msg, errReceive := protocol.ReceiveMessage()
		if errReceive != nil || msg == "Error\n" {
			log.Criticalf(
				"action: apuesta_enviada | result: fail | dni: %v | numero: %v", c.data.Document, c.data.Number,
			)
		} else {
			log.Infof(
				"action: apuesta_enviada | result: success | dni: %v | numero: %v", c.data.Document, c.data.Number,
			)
		}

	} else {
		log.Criticalf(
			"action: send | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}

	c.conn.Close()
}

// handleSignals Handles graceful shutdown on SIGTERM or SIGINT
func (c *Client) handleSignals() {
	<-c.signalChan

	if c.conn != nil {
		c.conn.Close()
	}

	c.closeChan <- true
}
