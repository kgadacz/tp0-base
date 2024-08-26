#!/bin/bash

SERVER_CONTAINER_NAME="server"

# Mensaje de prueba
TEST_MESSAGE="Testeando server"

# Nombre del contenedor temporal para ejecutar netcat
NC_CONTAINER_NAME="nc_test"

# Ejecutar el comando netcat desde otro contenedor en la misma red
RESULT=$(docker run --rm --network container:${SERVER_CONTAINER_NAME} busybox:latest sh -c "echo '${TEST_MESSAGE}' | nc localhost 12345")

if [ "${RESULT}" == "${TEST_MESSAGE}" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
