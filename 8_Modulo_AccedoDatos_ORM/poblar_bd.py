from modelos_orm import Order, OrderItem, User
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# 1. Nos conectamos a nuestra base de datos real (la que creó Alembic)
engine = create_engine("sqlite:///mi_base_de_datos.db", echo=True)

# 2. Iniciamos la sesión para poder hacer transacciones
print("\n--- INICIANDO INSERCIÓN DE DATOS ---\n")
with Session(engine) as session:

    # Creamos el primer usuario con sus datos
    usuario_1 = User(
        name="Carlos Dev",
        email="carlos@ejemplo.com",
        orders=[
            Order(
                items=[
                    OrderItem(product_name="Monitor 27'", price=350.00),
                    OrderItem(product_name="Teclado Mecánico", price=85.50),
                ]
            )
        ],
    )

    # Creamos el segundo usuario con sus datos
    usuario_2 = User(
        name="Laura Data",
        email="laura@ejemplo.com",
        orders=[
            Order(items=[OrderItem(product_name="Libro Python Pro", price=45.00)]),
            Order(items=[OrderItem(product_name="Suscripción Nube", price=12.99)]),
        ],
    )

    # Agregamos los objetos a la sesión
    session.add(usuario_1)
    session.add(usuario_2)

    # ¡Hacemos COMMIT para guardar todo permanentemente en la base de datos!
    session.commit()
    print("\n✅ ¡Datos de prueba insertados con éxito!\n")
