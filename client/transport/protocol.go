package transport

import (
	"net"
	"fmt"
	"encoding/binary"
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/constants"
	"io"

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

	err := binary.Write(p.conn, binary.BigEndian, uint16(length))
    if err != nil {
        return fmt.Errorf("error writing message length to connection: %w", err)
    }

    _, err = io.WriteString(p.conn, msg)
    if err != nil {
        return fmt.Errorf("error writing message to connection: %w", err)
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