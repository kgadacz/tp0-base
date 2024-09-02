#!/bin/bash

# Verificar que se hayan pasado los parámetros correctos
if [ "$#" -ne 2 ]; then
  echo "Se debe ingresar: $0 <nombre_archivo_salida> <cantidad_clientes>"
  exit 1
fi

# Parámetros
OUTPUT_FILE=$1
NUM_CLIENTS=$2

# Validar que la cantidad de clientes sea un numero entero
if ! [[ "$NUM_CLIENTS" =~ ^[0-9]+$ ]]; then
  echo "Error: La cantidad de clientes debe ser un número entero."
  exit 1
fi

echo "Nombre del archivo de salida: $OUTPUT_FILE"
echo "Cantidad de clientes: $NUM_CLIENTS"

# Llamar al script de Python para generar el archivo
python generar_docker_compose.py $OUTPUT_FILE $NUM_CLIENTS