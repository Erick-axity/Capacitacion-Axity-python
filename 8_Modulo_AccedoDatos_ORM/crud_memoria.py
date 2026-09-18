from modelos_orm import Base, Order, OrderItem, User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# =====================================================================
# 1. SQLITE EN MEMORIA
# =====================================================================
# 'sqlite:///:memory:' crea una base de datos temporal en la RAM.
# 'echo=True' imprimirá en consola el SQL real que SQLAlchemy genera por debajo.
engine = create_engine("sqlite:///mi_base_de_datos.db", echo=True)

# Creamos las tablas en la RAM basándonos en nuestras clases
Base.metadata.create_all(engine)

# =====================================================================
# 2. TRANSACCIONES Y CRUD (Create, Read, Update, Delete)
# =====================================================================
print("\n--- INICIANDO SESIÓN CRUD ---\n")
with Session(engine) as session:

    # ---------------------------------
    # A. CREATE (Insertar datos)
    # ---------------------------------
    # Mágicamente, podemos crear el usuario, su orden y los items de un solo golpe
    nuevo_usuario = User(
        name="Ana Pérez",
        email="ana@empresa.com",
        orders=[
            Order(
                items=[
                    OrderItem(product_name="Laptop", price=1200.50),
                    OrderItem(product_name="Mouse", price=25.00),
                ]
            )
        ],
    )

    session.add(nuevo_usuario)
    session.commit()  # TRANSACCIÓN: Guarda los cambios en la DB
    print("\n✅ Datos creados exitosamente.\n")

    # ---------------------------------
    # B. READ (Consultas con relaciones)
    # ---------------------------------
    # Buscamos a la usuaria Ana
    consulta = select(User).where(User.name == "Ana Pérez")
    ana_db = session.execute(consulta).scalar_one()

    print(f"👤 Usuario encontrado: {ana_db}")
    for orden in ana_db.orders:
        print(f"  📦 Orden ID: {orden.id}")
        for item in orden.items:
            print(f"    - Item: {item.product_name} (${item.price})")

    # ---------------------------------
    # C. UPDATE (Actualizar datos)
    # ---------------------------------
    ana_db.name = "Ana P. (Actualizada)"
    session.commit()
    print("\n✅ Nombre actualizado.\n")

    # ---------------------------------
    # D. DELETE (Borrar en cascada)
    # ---------------------------------
    # Al borrar a Ana, el 'cascade="all, delete-orphan"' borrará también sus órdenes y items
    session.delete(ana_db)
    session.commit()
    print("\n✅ Usuario y dependencias borradas en cascada.\n")

print("--- FIN DEL CRUD ---")
