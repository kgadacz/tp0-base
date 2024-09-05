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

* Cuando un cliente desea enviar un mensaje, primero envía la longitud del mensaje (como un entero de 2 bytes en formato Big Endian), seguido del contenido del mensaje. Esto asegura que el servidor pueda leer el mensaje completo sin problemas de lectura corta.
* Cuando el servidor envía un mensaje, también envía primero la longitud del mensaje (como un entero de 2 bytes en formato Big Endian) y luego el mensaje en sí. De esta manera se asegura no tener problemas de lectura corta

Para enviar los bets se utiliza el siguiente formato:
Para enviar los bets se utiliza el siguiente formato:

    NroAgencia,Nombre,Apellido,Documento,FechaNacimiento,NroApostado

Es decir, los datos estan separados por comas y en ese orden.

Los paquetes que envia el cliente como el servidor pueden ser de a lo sumo 8kb.

### Ejercicio N°6:

Para adaptar la logica a lo pedido en este ejercicio, es decir, el envio por chunks, el cliente envia un primer paquete indicando la cantidad de chunks que va a recibir el servidor. Esto lo utiliza el servidor para saber cuantos chunks esperar. Luego el protocolo continua igual que lo descripto en el ejercicio 5

Cuando se debe enviar por chunks, los bets son concatenados por ";" y en el servidor se utilizara eso para poder separar cada bet.

### Ejercicio N°7:

Para este ejercicio cuando un cliente termina de enviar todos sus bets, el servidor aumenta su contador interno donde indica la cantidad de clientes que terminaron de mandar sus bets. En configuracion tiene una variable la cual indica cuantos clientes debe esperar antes de poder revelar los resultados del sorteo. Para el cliente se utilizo una logica donde al preguntar por los resultados del sorteo, si los mismos aun no estan disponibles (el servidor le envia un REFUSED), el mismo vuelve a preguntar hasta que obtiene un resultado satisfactorio (listado de los DNIs que ganaron)

### Ejercicio N°8:

Para la sincronizacion se utilizo el módulo multiprocessing el cual permite ejecutar múltiples procesos en paralelo a diferencia de los hilos (threads), que en Python están limitados por el Global Interpreter Lock (GIL).

Utilizando multiprocessing, cada proceso tiene su propia memoria, lo que significa que no comparten estado de manera directa, a diferencia de los hilos.

Ademas se utilizo locks para restringir las secciones criticas como por ejemplo el guardado de bets y la cantidad de clientes que terminaron de procesar sus bets.