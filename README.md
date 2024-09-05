# TP0: Docker + Comunicaciones + Concurrencia

## Instrucciones de uso
### Ejercicio N°1:

Para generar el archivo docker compose se debe correr el comando: 
* **./generar-compose.sh docker-compose-dev.yaml cantidad_clientes**

donde el primer parametro indica como se va a llamar el archivo docker-compose que se va a generar y el segundo indica la cantidad de clientes con la cual se va a generar el archivo docker-compose. Un ejemplo de como ejecutarlo es: **./generar-compose.sh docker-compose-dev.yaml 5**

Una vez generado el archivo docker compose, puede correrse el script.sh que se adjunta el cual corre internamente los siguientes comandos:
* docker compose -f docker-compose-dev.yaml down
* docker build -f ./server/Dockerfile -t "server:latest" .
* docker build -f ./client/Dockerfile -t "client:latest" .
* docker compose -f docker-compose-dev.yaml up -d --build

Finalmente para ver los logs se puede hacer con:
* docker logs server
* docker logs clientX (donde X viene a ser el numero del cliente, por ejemplo client1)

### Ejercicio N°5:

Protocolo de comunicación implementado:

* Cuando un cliente desea enviar un mensaje, primero envía la longitud del mensaje (como un entero de 2 bytes en formato Big Endian), seguido del contenido del mensaje. Esto asegura que el servidor pueda leer el mensaje completo sin problemas de lectura corta.
* Cuando el servidor envía un mensaje, también envía primero la longitud del mensaje (como un entero de 2 bytes en formato Big Endian) y luego el mensaje en sí. De esta manera se asegura no tener problemas de lectura corta

Para enviar los bets se utiliza el siguiente formato:

    NroAgencia,Nombre,Apellido,Documento,FechaNacimiento,NroApostado

Es decir, los datos estan separados por comas y en ese orden.

Los paquetes que envia el cliente como el servidor pueden ser de a lo sumo 8kb.