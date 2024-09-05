package transport

import (
	"encoding/binary"
	"fmt"
	"io"
	"net"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/constants"
)

type Protocol struct {
	conn net.Conn
}

func NewProtocol(conn net.Conn) *Protocol {
	return &Protocol{conn: conn}
}

func (p *Protocol) SendMessage(msg string) error {
	length := len(msg)
	if length > constants.MAX_MESSAGE_LENGTH {
		return fmt.Errorf("message too long: length is %d bytes, but max is %d", length, constants.MAX_MESSAGE_LENGTH)
	}

	// Convert length to a 2-byte integer in Big Endian format
	lengthBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(lengthBytes, uint16(length))

	// Ensure all bytes are sent
	_, err := p.conn.Write(lengthBytes)
	if err != nil {
		return fmt.Errorf("error writing message length to connection: %w", err)
	}

	// Ensure the entire message is sent
	_, err = io.WriteString(p.conn, msg)
	if err != nil {
		return fmt.Errorf("error writing message to connection: %w", err)
	}

	return nil
}

func (p *Protocol) SendMessageChunks(msg int) error {
	// Create a buffer to hold the byte representation of the integer
	buf := make([]byte, 4) // Using 4 bytes for int (assuming 32-bit integer)

	// Convert the integer to bytes in big-endian order
	binary.BigEndian.PutUint32(buf, uint32(msg))

	// Send the byte slice to the connection
	_, err := p.conn.Write(buf)
	if err != nil {
		return fmt.Errorf("error writing amount of chunks: %w", err)
	}

	return nil
}

func (p *Protocol) ReceiveMessage() (string, error) {
	// Read the length of the message (2 bytes)
	lengthBytes := make([]byte, 2)
	_, err := io.ReadFull(p.conn, lengthBytes)
	if err != nil {
		return "", fmt.Errorf("error reading message length from connection: %w", err)
	}

	// Convert the length from bytes to integer
	length := binary.BigEndian.Uint16(lengthBytes)

	// Read the message based on the length
	messageBytes := make([]byte, length)
	_, err = io.ReadFull(p.conn, messageBytes)
	if err != nil {
		return "", fmt.Errorf("error reading message from connection: %w", err)
	}

	// Convert message bytes to string
	message := string(messageBytes)

	return message, nil
}