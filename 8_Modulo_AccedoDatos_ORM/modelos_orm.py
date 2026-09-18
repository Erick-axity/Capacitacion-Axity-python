from typing import List

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# 1. CLASE BASE: Todas nuestras tablas heredarán de aquí
class Base(DeclarativeBase):
    pass


# =====================================================================
# 2. MODELADO DE ENTIDADES Y RELACIONES
# =====================================================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    telefono: Mapped[str] = mapped_column(String(20), nullable=True)

    # RELACIÓN: 1 Usuario -> Muchas Órdenes
    orders: Mapped[List["Order"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(name='{self.name}', email='{self.email}')>"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    # LLAVE FORÁNEA: Conecta la orden con el usuario
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # RELACIONES BI-DIRECCIONALES
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user_id={self.user_id})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

    product_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)

    order: Mapped["Order"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return f"<OrderItem(product='{self.product_name}', price={self.price})>"
