import grpc

# Importamos los traductores
import orders_pb2
import orders_pb2_grpc


def run():
    print("🔌 Conectando al servidor gRPC...")

    # Abrimos un canal de comunicación directo al puerto 50051
    with grpc.insecure_channel("localhost:50051") as channel:
        # Creamos el 'Stub' (el cliente)
        stub = orders_pb2_grpc.OrderServiceStub(channel)

        # Construimos el mensaje usando la clase generada por el .proto
        peticion = orders_pb2.OrderRequest(product_id="LAPTOP-PRO", quantity=2)

        print("Enviando petición gRPC...")
        # Disparamos la función remota (RPC)
        respuesta = stub.CreateOrder(peticion)

        print(
            f"Respuesta del servidor -> ID Generado: {respuesta.order_id} | Status: {respuesta.status}"
        )


if __name__ == "__main__":
    run()
