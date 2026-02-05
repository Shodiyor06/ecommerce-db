from interfaces.cli import (
    show_home_menu,
    show_user_menu,
    show_products_table,
    show_cart_table,
    show_orders_table,
    show_order_details,
    show_success,
    show_error,
    show_info,
)


class MenuHandler:

    def __init__(self, app):
        self.app = app

    def show_main_menu(self):
        while True:
            show_home_menu()
            choice = input("\n→ Tanlovingizni kiriting: ").strip()

            if choice == "1":
                self.handle_register()
            elif choice == "2":
                self.handle_login()
            elif choice == "0":
                self.app.shutdown()
                break
            else:
                show_error("Noto'g'ri tanlov")

    def handle_register(self):
        print()
        username = input("Foydalanuvchi nomi: ").strip()
        password = input("Parol: ").strip()
        first_name = input("Ism: ").strip()
        last_name = input("Familiya: ").strip()

        success, message = self.app.user_service.create_user(
            username, password, first_name, last_name
        )

        if success:
            show_success(message)
        else:
            show_error(message)

    def handle_login(self):
        print()
        username = input("Foydalanuvchi nomi: ").strip()
        password = input("Parol: ").strip()

        success, message = self.app.user_service.login(username, password)

        if success:
            show_success(message)
            self.show_user_menu()
        else:
            show_error(message)

    def show_user_menu(self):
        while self.app.user_service.is_logged_in():
            username = self.app.user_service.logged_user.username
            user_id = self.app.user_service.logged_user.id
    
            show_user_menu(username)
            choice = input("\n→ Tanlovingizni kiriting: ").strip()
    
            if choice == "1":
                self.view_all_products()
            elif choice == "2":
                self.add_to_cart()
            elif choice == "3":
                self.view_cart()
            elif choice == "4":
                self.remove_from_cart()
            elif choice == "5":
                self.create_order()
            elif choice == "6":
                self.view_my_orders()
            elif choice == "7":
                self.add_product(user_id)          # ✅ YANGI
            elif choice == "8":
                self.manage_my_products(user_id)  # oldingi joyi
            elif choice == "0":
                self.app.user_service.logout()
                show_success("Chiqib ketdiniz")
            else:
                show_error("Noto'g'ri tanlov")

    def view_all_products(self):
        products = self.app.product_service.get_all_products()
        if not products:
            show_info("Hech qanday mahsulot yo'q")
            return
        show_products_table(products)

    def add_to_cart(self):
        products = self.app.product_service.get_all_products()

        if not products:
            show_error("Mahsulot yo'q")
            return

        show_products_table(products)

        try:
            product_id = int(input("\nMahsulot ID: "))
            quantity = int(input("Miqdor: "))

            user_id = self.app.user_service.logged_user.id
            success, message = self.app.cart_service.add_to_cart(
                user_id, product_id, quantity
            )

            if success:
                show_success(message)
            else:
                show_error(message)
        except ValueError:
            show_error("Raqam kiriting")

    def view_cart(self):
        user_id = self.app.user_service.logged_user.id
        cart_items = self.app.cart_service.get_cart_items(user_id)
        show_cart_table(cart_items)

    def remove_from_cart(self):
        user_id = self.app.user_service.logged_user.id
        cart_items = self.app.cart_service.get_cart_items(user_id)

        if not cart_items:
            show_error("Savat bo'sh")
            return

        show_cart_table(cart_items)

        try:
            product_id = int(input("\nO'chiriladigan mahsulot ID: "))
            success, message = self.app.cart_service.remove_from_cart(
                user_id, product_id
            )

            if success:
                show_success(message)
            else:
                show_error(message)
        except ValueError:
            show_error("Raqam kiriting")

    def create_order(self):
        user_id = self.app.user_service.logged_user.id
        success, message, order_id = self.app.order_service.create_order(user_id)

        if success:
            show_success(message)
            order_details = self.app.order_service.get_order_details(order_id)
            show_order_details(order_details)
        else:
            show_error(message)

    def view_my_orders(self):
        user_id = self.app.user_service.logged_user.id
        orders = self.app.order_service.get_user_orders(user_id)

        if not orders:
            show_info("Sizda hech qanday buyurtma yo'q")
            return

        show_orders_table(orders)

        try:
            order_id = int(input("\nOrder ID (detallari uchun): "))
            order_details = self.app.order_service.get_order_details(order_id)
            if order_details:
                show_order_details(order_details)
            else:
                show_error("Order topilmadi")
        except ValueError:
            pass

    def manage_my_products(self, user_id: str):
        while True:
            products = self.app.product_service.get_user_products(user_id)

            print("\n" + "=" * 60)
            print("📦 MENING MAHSULOTLARIM")
            print("=" * 60)

            if products:
                show_products_table(products)
            else:
                print("Sizning mahsulotingiz yo'q\n")

            print("1. Mahsulot qo'shish")
            print("2. Mahsulotni yangilash")
            print("3. Mahsulotni o'chirish")
            print("0. Orqaga")

            choice = input("\n→ Tanlovingizni kiriting: ").strip()

            if choice == "1":
                self.add_product(user_id)
            elif choice == "2":
                self.edit_product(user_id)
            elif choice == "3":
                self.delete_product(user_id)
            elif choice == "0":
                break
            else:
                show_error("Noto'g'ri tanlov")

    def add_product(self, user_id: str):
        print()
        try:
            name = input("Mahsulot nomi: ").strip()
            category = input("Kategoriya: ").strip()
            price = float(input("Narx (so'm): "))
            stock = int(input("Stock: "))
            description = input("Tavsif: ").strip()

            success, message = self.app.product_service.create_product(
                user_id, name, category, price, stock, description
            )

            if success:
                show_success(message)
            else:
                show_error(message)
        except ValueError:
            show_error("To'g'ri formatda kiriting")

    def edit_product(self, user_id: str):
        products = self.app.product_service.get_user_products(user_id)
        if not products:
            show_error("Mahsulotingiz yo'q")
            return

        show_products_table(products)

        try:
            product_id = int(input("\nYangilanish uchun product ID: "))

            print("\nQaysi fieldni o'zgartirasiz? (bo'sh qoldirsa skip)")
            name = input("Yangi nomi: ").strip()
            category = input("Yangi kategoriya: ").strip()
            price_str = input("Yangi narx: ").strip()
            stock_str = input("Yangi stock: ").strip()
            description = input("Yangi tavsif: ").strip()

            updates = {}
            if name:
                updates["name"] = name
            if category:
                updates["category"] = category
            if price_str:
                updates["price"] = float(price_str)
            if stock_str:
                updates["stock"] = int(stock_str)
            if description:
                updates["description"] = description

            if not updates:
                show_info("Hech qanday o'zgarish kiritilmadi")
                return

            success, message = self.app.product_service.update_product(
                product_id, user_id, **updates
            )

            if success:
                show_success(message)
            else:
                show_error(message)
        except ValueError:
            show_error("To'g'ri formatda kiriting")

    def delete_product(self, user_id: str):
        products = self.app.product_service.get_user_products(user_id)
        if not products:
            show_error("Mahsulotingiz yo'q")
            return

        show_products_table(products)

        try:
            product_id = int(input("\nO'chiriladigan product ID: "))
            success, message = self.app.product_service.delete_product(
                product_id, user_id
            )

            if success:
                show_success(message)
            else:
                show_error(message)
        except ValueError:
            show_error("Raqam kiriting")
