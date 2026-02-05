from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)

    products = relationship(
        "Product",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    cart = relationship(
        "Cart", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    orders = relationship(
        "Order", back_populates="user", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    description = Column(String, default="")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    owner = relationship("User", back_populates="products")

    cart_items = relationship(
        "CartItem", back_populates="product", cascade="all, delete-orphan"
    )
    order_items = relationship(
        "OrderItem", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Product(name='{self.name}', price={self.price}, stock={self.stock})>"

    def get_final_price(self):
        discount = (self.price * self.sale) / 100
        return self.price - discount

    def can_sell(self, quantity: int) -> bool:
        return self.stock >= quantity


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="cart")
    items = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Cart(user_id='{self.user_id}', items_count={len(self.items)})>"

    def get_total_price(self):
        total = 0
        for item in self.items:
            total += item.get_total_price()
        return total

    def get_items_count(self):
        return sum(item.quantity for item in self.items)

    def is_empty(self):
        return len(self.items) == 0


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    def __repr__(self):
        return f"<CartItem(product='{self.product.name}', qty={self.quantity})>"

    def get_total_price(self):
        return self.product.get_final_price() * self.quantity


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    total_price = Column(Float, default=0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order(id={self.id}, user='{self.user.username}', total={self.total_price})>"

    def recalculate_total(self):
        self.total_price = sum(item.get_total_price() for item in self.items)

    def get_items_count(self):
        return sum(item.quantity for item in self.items)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price_at_purchase = Column(Float, nullable=False)
    sale_at_purchase = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(product='{self.product.name}', qty={self.quantity})>"

    def get_total_price(self):
        discount = (self.price_at_purchase * self.sale_at_purchase) / 100
        final_price = self.price_at_purchase - discount
        return final_price * self.quantity
