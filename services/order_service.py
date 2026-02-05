from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from models import Cart, CartItem, Order, OrderItem, Product, User


class OrderService:

    def __init__(self, session: Session):
        self.session = session

    def create_order(self, user_id: str) -> tuple[bool, str, Optional[int]]:
        try:

            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Foydalanuvchi topilmadi", None

            cart = self.session.query(Cart).filter(Cart.user_id == user_id).first()
            if not cart:
                return False, "Savat topilmadi", None

            if cart.is_empty():
                return False, "Savat bo'sh. Mahsulot qo'shib oling", None

            order = Order(user_id=user_id)
            self.session.add(order)
            self.session.flush()

            for cart_item in cart.items:
                product = cart_item.product

                if not product.can_sell(cart_item.quantity):
                    self.session.rollback()
                    return False, f"'{product.name}' uchun yetarli stock yok", None

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    price_at_purchase=product.price,
                    sale_at_purchase=product.sale,
                )
                self.session.add(order_item)

                product.stock -= cart_item.quantity

            order.recalculate_total()

            self.session.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

            self.session.commit()

            return True, f"Order #{order.id} muvaffaqiyatli yaratildi", order.id

        except Exception as e:
            self.session.rollback()
            return False, f"Order yaratishda xato: {str(e)}", None

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.session.query(Order).filter(Order.id == order_id).first()

    def get_user_orders(self, user_id: str) -> List[Order]:
        return (
            self.session.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def get_all_orders(self) -> List[Order]:
        return self.session.query(Order).order_by(Order.created_at.desc()).all()

    def update_order_status(self, order_id: int, status: str) -> tuple[bool, str]:
        valid_statuses = ["pending", "completed", "cancelled"]

        if status not in valid_statuses:
            return False, f"Noto'g'ri status. Mumkin: {', '.join(valid_statuses)}"

        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return False, "Order topilmadi"

            old_status = order.status
            order.status = status
            self.session.commit()

            return True, f"Status '{old_status}' dan '{status}' ga o'zgartirildi"

        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {str(e)}"

    def cancel_order(self, order_id: int) -> tuple[bool, str]:
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                return False, "Order topilmadi"

            if order.status == "cancelled":
                return False, "Bu order allaqachon bekor qilingan"

            for order_item in order.items:
                order_item.product.stock += order_item.quantity

            order.status = "cancelled"
            self.session.commit()

            return True, f"Order #{order.id} bekor qilindi va stock qaytarildi"

        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {str(e)}"

    def get_order_details(self, order_id: int) -> dict:
        order = self.get_order_by_id(order_id)

        if not order:
            return {}

        return {
            "id": order.id,
            "user": order.user.full_name(),
            "status": order.status,
            "total_price": order.total_price,
            "items_count": order.get_items_count(),
            "created_at": order.created_at,
            "items": [
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price_at_purchase": item.price_at_purchase,
                    "sale": item.sale_at_purchase,
                    "total": item.get_total_price(),
                }
                for item in order.items
            ],
        }

    def get_revenue(self, status: str = "completed") -> float:
        orders = self.session.query(Order).filter(Order.status == status).all()

        return sum(order.total_price for order in orders)