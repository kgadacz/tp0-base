import sys

def generar_docker_compose(output_file, num_clients):
    compose_base = """name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    volumes:
      - ./server/config.ini:/config.ini
    networks:
      - testing_net
"""

    # Generar servicios de cliente
    client_services = ""
    for i in range(1, int(num_clients) + 1):
        client_services += f"""
  client{i}:
    container_name: client{i}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={i}
      - CLI_LOG_LEVEL=DEBUG
    volumes:
      - ./client/config.yaml:/config.yaml
    networks:
      - testing_net
    depends_on:
      - server
"""

    networks = """
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""

    docker_compose_content = compose_base + client_services + networks

    with open(output_file, 'w') as f:
        f.write(docker_compose_content)

    print(f"{output_file} generado con {num_clients} clientes.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Se debe ingresar: python3 generar_docker_compose.py <nombre_archivo_salida> <cantidad_clientes>")
        sys.exit(1)

    output_file = sys.argv[1]
    num_clients = sys.argv[2]
    
    generar_docker_compose(output_file, num_clients)
