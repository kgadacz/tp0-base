package common

import (
	"encoding/csv"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/constants"
)

type CSVChunkReader struct {
	reader    *csv.Reader
	file      *os.File
	block     strings.Builder
	lineCount int
	maxAmount int
	id        string
}

func NewCSVChunkReader(fileName string, maxAmount int, id string) (*CSVChunkReader, error) {
	file, err := os.Open(fileName)
	if err != nil {
		fmt.Printf("Error opening file: %v\n", err)
		return nil, err
	}

	reader := csv.NewReader(file)
	return &CSVChunkReader{
		reader:    reader,
		file:      file,
		block:     strings.Builder{},
		lineCount: 0,
		maxAmount: maxAmount,
		id:        id,
	}, nil
}

// GetNextChunk returns the next chunk of CSV lines prefixed with the id, up to maxAmount
func (r *CSVChunkReader) GetNextChunk() (string, int, error) {
	r.block.Reset()
	lineCount := 0

	for lineCount < r.maxAmount {
		record, err := r.reader.Read()
		if err == io.EOF {
			if lineCount > 0 {
				return r.block.String(), lineCount, nil
			}
			return "", 0, err // No more data
		}
		if err != nil {
			fmt.Printf("Error reading CSV: %v\n", err)
			return "", 0, err
		}

		// Add id as prefix to the line and concatenate it with ";"
		prefixedLine := r.id + "," + recordToString(record)
		if lineCount > 0 {
			r.block.WriteString(";")
		}
		r.block.WriteString(prefixedLine)
		lineCount++

		if r.block.Len() > constants.MAX_MESSAGE_LENGTH {
			return "", 0, fmt.Errorf("chunk too large")
		}
	}

	return r.block.String(), lineCount, nil
}

// recordToString converts a CSV record (slice of strings) to a single string
func recordToString(record []string) string {
	return strings.Join(record, ",")
}

// Close the file when done
func (r *CSVChunkReader) Close() {
	r.file.Close()
}
