from sqlalchemy.orm import Session
from models import User, Cart
from utils.validators import validate_name
from utils.security import hash_password, verify_password
from typing import Optional


class UserService:

    def __init__(self, session: Session):
        self.session = session
        self.logged_user: Optional[User] = None

    def user_exists(self, username: str) -> bool:
        user = self.session.query(User).filter(User.username == username).first()
        return user is not None

    def create_user(self, username: str, password: str, first_name: str, last_name: str) -> tuple[bool, str]:

        if not username or len(username) < 3:
            return False, "Username kamida 3 ta belgidan iborat bo'lishi kerak"

        if not validate_name(first_name):
            return False, "Ism faqat harflardan iborat bo'lishi kerak"

        if not validate_name(last_name):
            return False, "Familiya faqat harflardan iborat bo'lishi kerak"

        if len(password) < 4:
            return False, "Parol kamida 4 ta belgidan iborat bo'lishi kerak"


        if self.user_exists(username):
            return False, f"'{username}' nomli user allaqachon mavjud"

        try:

            new_user = User(
                username=username.lower(),
                password=hash_password(password),
                first_name=first_name.capitalize(),
                last_name=last_name.capitalize()
            )

            self.session.add(new_user)
            self.session.flush()


            cart = Cart(user_id=new_user.id)
            self.session.add(cart)

            self.session.commit()
            return True, "Siz muvaffaqiyatli ro'yxatdan o'tdingiz ✓"

        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {str(e)}"

    def login(self, username: str, password: str) -> tuple[bool, str]:
        try:
            user = self.session.query(User).filter(
                User.username == username.lower()
            ).first()

            if not user:
                return False, "Foydalanuvchi topilmadi"

            if not verify_password(password, user.password):
                return False, "Parol noto'g'ri"

            self.logged_user = user
            return True, f"Xush kelibsiz, {user.username}"

        except Exception as e:
            return False, f"Login xatosi: {str(e)}"

    def logout(self) -> bool:
        if self.logged_user:
            self.logged_user = None
            return True
        return False

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(
            User.username == username.lower()
        ).first()

    def is_logged_in(self) -> bool:
        return self.logged_user is not None

    def delete_user(self, user_id: str) -> tuple[bool, str]:
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "Foydalanuvchi topilmadi"

            self.session.delete(user)
            self.session.commit()
            return True, "Foydalanuvchi o'chirildi"
        except Exception as e:
            self.session.rollback()
            return False, f"Xato: {str(e)}"