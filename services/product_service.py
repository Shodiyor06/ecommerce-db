from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Product


class ProductService:
    def __init__(self, session: Session):
        self.session = session

    def create_product(
        self,
        user_id: str,
        name: str,
        category: str,
        price: float,
        stock: int,
        description: str = "",
    ) -> Tuple[bool, str]:
        if not name or len(name.strip()) < 3:
            return False, "Mahsulot nomi kamida 3 ta belgidan iborat bo'lishi kerak"

        if not category or len(category.strip()) < 2:
            return False, "Kategoriya noto'g'ri"

        if price <= 0:
            return False, "Narx 0 dan katta bo'lishi kerak"

        if stock < 0:
            return False, "Stock manfiy bo'lishi mumkin emas"

        try:
            product = Product(
                user_id=user_id,
                name=name.strip(),
                category=category.strip(),
                price=price,
                stock=stock,
                description=description.strip(),
                is_active=True,
            )

            self.session.add(product)
            self.session.commit()

            return True, f"Mahsulot '{product.name}' qo'shildi (ID: {product.id})"
        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {e}"

    def get_user_products(self, user_id: str) -> List[Product]:
        return (
            self.session.query(Product)
            .filter(Product.user_id == user_id, Product.is_active.is_(True))
            .order_by(Product.name)
            .all()
        )

    def get_all_products(self) -> List[Product]:
        return (
            self.session.query(Product)
            .filter(Product.is_active.is_(True))
            .order_by(Product.name)
            .all()
        )

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return (
            self.session.query(Product)
            .filter(Product.id == product_id, Product.is_active.is_(True))
            .first()
        )

    def update_product(
        self,
        product_id: int,
        user_id: str,
        **kwargs,
    ) -> Tuple[bool, str]:
        try:
            product = self.session.query(Product).filter(Product.id == product_id).first()

            if not product or not product.is_active:
                return False, "Mahsulot topilmadi"

            if product.user_id != user_id:
                return False, "Faqat o'z mahsulotingizni o'zgartira olasiz"

            allowed_fields = {"name", "category", "price", "stock", "description"}

            for key, value in kwargs.items():
                if key not in allowed_fields:
                    continue

                if key == "name" and len(value.strip()) < 3:
                    return False, "Mahsulot nomi kamida 3 ta belgi bo'lishi kerak"

                if key == "price" and value <= 0:
                    return False, "Narx 0 dan katta bo'lishi kerak"

                if key == "stock" and value < 0:
                    return False, "Stock manfiy bo'lishi mumkin emas"

                setattr(product, key, value)

            self.session.commit()
            return True, f"Mahsulot '{product.name}' yangilandi"
        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {e}"

    def delete_product(self, product_id: int, user_id: str) -> Tuple[bool, str]:
        try:
            product = self.session.query(Product).filter(Product.id == product_id).first()

            if not product or not product.is_active:
                return False, "Mahsulot topilmadi"

            if product.user_id != user_id:
                return False, "Faqat o'z mahsulotingizni o'chira olasiz"

            product.is_active = False
            self.session.commit()

            return True, f"Mahsulot '{product.name}' o'chirildi"
        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {e}"

    def search_products(self, query_text: str) -> List[Product]:
        return (
            self.session.query(Product)
            .filter(
                Product.is_active.is_(True),
                or_(
                    Product.name.ilike(f"%{query_text}%"),
                    Product.description.ilike(f"%{query_text}%"),
                ),
            )
            .all()
        )

    def get_products_by_category(self, category: str) -> List[Product]:
        return (
            self.session.query(Product)
            .filter(
                Product.is_active.is_(True),
                Product.category.ilike(category),
            )
            .all()
        )

    def update_stock(self, product_id: int, quantity: int) -> Tuple[bool, str]:
        try:
            product = self.get_product_by_id(product_id)

            if not product:
                return False, "Mahsulot topilmadi"

            new_stock = product.stock + quantity

            if new_stock < 0:
                return False, f"Yetarli stock yo'q. Mavjud: {product.stock}"

            product.stock = new_stock
            self.session.commit()

            return True, f"Stock yangilandi: {new_stock}"
        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {e}"