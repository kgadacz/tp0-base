package common

import (
	"net"
	"os"
	"os/signal"
	"syscall"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/transport"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/constants"
	"strings"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type Client struct {
	config     ClientConfig
	conn       net.Conn
	signalChan chan os.Signal
	closeChan  chan bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:     config,
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



func (c *Client) StartSendingBets() error {
	// Create the connection to the server
	c.createClientSocket()
	id := os.Getenv("ID")
	protocol := transport.NewProtocol(c.conn)
	protocol.SendMessage(constants.SEND_BETS)
	fileName := "agency-" + id + ".csv"
	reader, err := NewCSVChunkReader(fileName, c.config.BatchMaxSize, id)
	if err != nil {
		return err
	}
	defer reader.Close()


	batch, size, err := reader.GetNextChunk()

	for size > 0 {
		protocol.SendMessage(batch)
		protocol.ReceiveMessage()
		batch, size, err = reader.GetNextChunk()
	}

	protocol.SendMessage(constants.END_CHUNKS_MESSAGE)
	respuesta,_ := protocol.ReceiveMessage()
	if respuesta == constants.ERROR_PROCESSING_CHUNKS {
		log.Criticalf("action: apuestas_enviadas | result: fail")
	} else {
		log.Infof("action: apuestas_enviadas | result: success")
	}
	c.conn.Close()
	return nil
}

// GetAmount splits the winners string by commas and returns the number of elements.
func GetAmount(winners string) int {
    // Split the string by comma
	if winners == constants.EMPTY {
		return 0
	}

    elements := strings.Split(winners, ",")
    return len(elements)
}

func (c *Client) StartAskingWinner() error {
	id := os.Getenv("ID")
	
	for {
		// Create the connection to the server
		c.createClientSocket()
		protocol := transport.NewProtocol(c.conn)
		protocol.SendMessage(constants.ASK_WINNER)
		protocol.SendMessage(id)
		winners, _ := protocol.ReceiveMessage()

		log.Debugf("action: dni_ganadores: %v", winners)
		c.conn.Close()
		if winners == constants.REFUSED {
			log.Infof("action: consulta_ganadores | result: refused")
		} else {
			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", GetAmount(winners))
			break
		}
	}

	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	c.StartSendingBets()
	c.StartAskingWinner()
}

// handleSignals Handles graceful shutdown on SIGTERM or SIGINT
func (c *Client) handleSignals() {
	<-c.signalChan

	if c.conn != nil {
		c.conn.Close()
	}

	c.closeChan <- true
}
