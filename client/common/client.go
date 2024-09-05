package common

import (
	"net"
	"os"
	"os/signal"
	"syscall"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/transport"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/constants"
	"github.com/op/go-logging"
	"strconv"
)

var log = logging.MustGetLogger("log")

type Client struct {
	config     ClientConfig
	data 	   []string
	conn       net.Conn
	signalChan chan os.Signal
	closeChan  chan bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, bets []string) *Client {
	client := &Client{
		config:     config,
		data:       bets,
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
	chunksAmount := len(c.data)
	chunksAmountString := strconv.Itoa((len(c.data)))
	protocol.SendMessage(chunksAmountString)
	for i := 0; i < chunksAmount; i++ {
		// Send each item in the data array
		item := c.data[i]
		protocol.SendMessage(item)
		_, err := protocol.ReceiveMessage()

		if err != nil {
			log.Criticalf(
				"action: send | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
		}
	}
	respuesta,_ := protocol.ReceiveMessage()
	if respuesta == constants.ERROR_PROCESSING_CHUNKS {
		log.Criticalf("action: apuestas_enviadas | result: fail")
	} else {
		log.Infof("action: apuestas_enviadas | result: success")
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
