package common

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
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

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		select {
		case <-c.closeChan:
			log.Infof("action: loop_interrupt | result: success | client_id: %v", c.config.ID)
			return
		default:
			// Create the connection to the server
			c.createClientSocket()

			// TODO: Modify the send to avoid short-write
			fmt.Fprintf(c.conn, "[CLIENT %v] Message N°%v\n", c.config.ID, msgID)
			msg, err := bufio.NewReader(c.conn).ReadString('\n')
			c.conn.Close()

			if err != nil {
				log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v", c.config.ID, err)
				return
			}

			log.Infof("action: receive_message | result: success | client_id: %v | msg: %v", c.config.ID, msg)

			// Wait a time between sending one message and the next one
			time.Sleep(c.config.LoopPeriod)
		}
	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

// handleSignals Handles graceful shutdown on SIGTERM or SIGINT
func (c *Client) handleSignals() {
	<-c.signalChan
	log.Infof("action: signal_received | result: graceful_shutdown | client_id: %v", c.config.ID)

	if c.conn != nil {
		c.conn.Close()
		log.Infof("action: close_connection | result: success | client_id: %v", c.config.ID)
	}

	c.closeChan <- true
}
