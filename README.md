# TP0: Docker + Comunicaciones + Concurrencia

## Instrucciones de uso
### Ejercicio N°1:

Para generar el archivo docker compose se debe correr el comando: 
* **./generar-compose.sh docker-compose-dev.yaml cantidad_clientes**

donde el primer parametro indica como se va a llamar el archivo docker-compose que se va a generar y el segundo indica la cantidad de clientes con la cual se va a generar el archivo docker-compose. Un ejemplo de como ejecutarlo es: **./generar-compose.sh docker-compose-dev.yaml 5**

### Ejercicio N°5:

Protocolo de comunicación implementado:
* Cuando un cliente desea enviar un mensaje primero debe enviar la longitud que va a tener el mismo y luego su contenido. De esta forma se asegura que no ocurre un short read del lado del servidor ya que sabe exactamente cuanto debe leer.
* Cuando el servidor desea enviar un mensaje se envia directamente sin enviar previamente la longitud del mismo y para identificar el fin del mensaje se utiliza \n

Los mensajes que envia el cliente tienen el siguiente formato:

    NroAgencia,Nombre,Apellido,Documento,FechaNacimiento,NroApostado

Es decir, los datos estan separados por comas y en ese orden.

Por otro lado, los mensajes que envia el servidor tienen el siguiente formato:

    Ok: Si pudo guardar la apuesta del cliente
    Error: Si hubo algun problema al guardar la apuesta del cliente

Los paquetes pueden ser de a lo sumo 8kb.