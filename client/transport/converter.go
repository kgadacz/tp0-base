package transport
import (
	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/domain"
	"fmt"
)

func ConvertClientDataToMessage(data domain.ClientData) string {
	return fmt.Sprintf(
		"%s,%s,%s,%s,%s,%s\n",
		data.Id,
		data.FirstName,
		data.LastName,
		data.Document,
		data.BirthDate,
		data.Number,
	)
}