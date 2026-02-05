from typing import List, Optional

from sqlalchemy.orm import Session

from models import Cart, CartItem, Product, User


class CartService:

    def __init__(self, session: Session):
        self.session = session

    def get_cart(self, user_id: str) -> Optional[Cart]:
        return self.session.query(Cart).filter(Cart.user_id == user_id).first()

    def add_to_cart(
        self, user_id: str, product_id: int, quantity: int = 1
    ) -> tuple[bool, str]:
        try:

            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Foydalanuvchi topilmadi"

            cart = self.get_cart(user_id)
            if not cart:
                return False, "Savat topilmadi"

            product = (
                self.session.query(Product).filter(Product.id == product_id).first()
            )

            if not product:
                return False, "Mahsulot topilmadi"

            if not product.is_active:
                return False, f"'{product.name}' hozirda sotilmayapti"

            if quantity <= 0:
                return False, "Miqdor 1 dan katta bo'lishi kerak"

            if not product.can_sell(quantity):
                return False, f"Yetarli stock yok. Mavjud: {product.stock}"

            cart_item = (
                self.session.query(CartItem)
                .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
                .first()
            )

            if cart_item:

                new_quantity = cart_item.quantity + quantity
                if not product.can_sell(new_quantity):
                    return False, f"Yetarli stock yok. Mavjud: {product.stock}"

                cart_item.quantity = new_quantity
                self.session.commit()
                return (
                    True,
                    f"'{product.name}' savatga qo'shildi (jami: {new_quantity} dona)",
                )
            else:

                new_item = CartItem(
                    cart_id=cart.id, product_id=product_id, quantity=quantity
                )
                self.session.add(new_item)
                self.session.commit()
                return True, f"'{product.name}' savatga qo'shildi"

        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {str(e)}"

    def remove_from_cart(self, user_id: str, product_id: int) -> tuple[bool, str]:
        try:
            cart = self.get_cart(user_id)
            if not cart:
                return False, "Savat topilmadi"

            cart_item = (
                self.session.query(CartItem)
                .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
                .first()
            )

            if not cart_item:
                return False, "Mahsulot savatda topilmadi"

            product_name = cart_item.product.name
            self.session.delete(cart_item)
            self.session.commit()

            return True, f"'{product_name}' savatdan olib tashlandi"

        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {str(e)}"

    def update_quantity(
        self, user_id: str, product_id: int, new_quantity: int
    ) -> tuple[bool, str]:
        try:
            if new_quantity <= 0:
                return self.remove_from_cart(user_id, product_id)

            cart = self.get_cart(user_id)
            if not cart:
                return False, "Savat topilmadi"

            cart_item = (
                self.session.query(CartItem)
                .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
                .first()
            )

            if not cart_item:
                return False, "Mahsulot savatda topilmadi"

            product = cart_item.product

            if not product.can_sell(new_quantity):
                return False, f"Yetarli stock yok. Mavjud: {product.stock}"

            cart_item.quantity = new_quantity
            self.session.commit()

            return True, f"Miqdor yangilandi: {new_quantity}"

        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {str(e)}"

    def clear_cart(self, user_id: str) -> tuple[bool, str]:
        try:
            cart = self.get_cart(user_id)
            if not cart:
                return False, "Savat topilmadi"

            self.session.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

            self.session.commit()
            return True, "Savat tozalandi"

        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {str(e)}"

    def get_cart_items(self, user_id: str) -> List[CartItem]:
        cart = self.get_cart(user_id)
        if not cart:
            return []

        return cart.items

    def get_cart_summary(self, user_id: str) -> dict:
        cart = self.get_cart(user_id)

        if not cart or cart.is_empty():
            return {"items_count": 0, "total_price": 0, "items": []}

        return {
            "items_count": cart.get_items_count(),
            "total_price": cart.get_total_price(),
            "items": cart.items,
        }