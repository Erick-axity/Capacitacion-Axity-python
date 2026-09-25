import json
import uuid
from concurrent import futures

import grpc

# Importamos los traductores autogenerados
import orders_pb2
import orders_pb2_grpc
import redis

# Conexión al Message Broker (Redis)
r = redis.Redis(host="localhost", port=6379, db=0)


# Implementamos la clase base que generó gRPC
class OrderServiceServicer(orders_pb2_grpc.OrderServiceServicer):

    def CreateOrder(self, request, context):
        print(
            f"[gRPC Servidor] Recibida orden: {request.quantity}x del producto '{request.product_id}'"
        )

        nuevo_id = str(uuid.uuid4())

        # =====================================================================
        # PUBLICAR EVENTO EN RABBITMQ / REDIS (Ecosistema mixto)
        # =====================================================================
        evento = {
            "event_type": "OrderCreated",
            "order_id": nuevo_id,
            "product_id": request.product_id,
        }

        try:
            # Publicamos el mensaje en el canal "events_channel"
            r.publish("events_channel", json.dumps(evento))
            print(
                f"[Redis] Evento 'OrderCreated' publicado exitosamente para el ID {nuevo_id}"
            )
        except redis.exceptions.ConnectionError:
            print(
                "[Redis] No detectado localmente. (Ignorando, pero la lógica gRPC continúa...)"
            )

        # Retornamos el objeto 'OrderReply' estricto definido en el .proto
        return orders_pb2.OrderReply(order_id=nuevo_id, status="SUCCESS")


def serve():
    # Levantamos un servidor gRPC con 10 "hilos" de trabajo
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrderServiceServicer_to_server(OrderServiceServicer(), server)

    # gRPC no usa el puerto 80, por defecto usa 50051
    server.add_insecure_port("[::]:50051")
    print("Servidor gRPC corriendo en el puerto 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
