import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from database import close_session, get_session, init_db
from interfaces.cli import show_error, show_success
from main_menu import MenuHandler
from services.cart_service import CartService
from services.order_service import OrderService
from services.product_service import ProductService
from services.user_service import UserService


class EcommerceApp:

    def __init__(self):
        try:
            init_db()
            self.session = get_session()

            self.user_service = UserService(self.session)
            self.product_service = ProductService(self.session)
            self.cart_service = CartService(self.session)
            self.order_service = OrderService(self.session)

            self.menu = MenuHandler(self)

        except Exception as e:
            show_error(f"Initialization xatosi: {str(e)}")
            sys.exit(1)

    def start(self):
        self.menu.show_main_menu()

    def shutdown(self):
        try:
            close_session(self.session)
            show_success("Dastur yopildi. Xayr!")
        except Exception as e:
            show_error(f"Shutdown xatosi: {str(e)}")
        finally:
            sys.exit(0)


def main():
    app = EcommerceApp()

    try:
        app.start()
    except KeyboardInterrupt:
        print()
        app.shutdown()
    except Exception as e:
        show_error(f"Dasturda xato: {str(e)}")
        app.shutdown()


if __name__ == "__main__":
    main()
