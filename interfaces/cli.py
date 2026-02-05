from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED

console = Console()


def show_home_menu():
    menu_text = """
[bold cyan]1.[/] Ro'yxatdan o'tish
[bold cyan]2.[/] Kirish
[bold cyan]0.[/] Chiqish
"""
    console.print(
        Panel(
            menu_text,
            title="[bold green] E-COMMERCE[/]",
            box=ROUNDED,
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


def show_user_menu(username: str):
    menu_text = f"""
[bold cyan]1.[/] Barcha mahsulotlarni ko'rish
[bold cyan]2.[/] Mahsulot qo'shish
[bold cyan]3.[/] Mahsulotlarni boshqarish
[bold cyan]4.[/] Savatga qo'shish
[bold cyan]5.[/] Savatni ko'rish
[bold cyan]6.[/] Savatdan o'chirish
[bold cyan]7.[/] Buyurtma yaratish
[bold cyan]8.[/] Buyurtmalarni ko'rish
[bold cyan]9.[/] Buyurtma statusini o'zgartirish
[bold cyan]0.[/] Chiqish

Foydalanuvchi: [bold yellow]{username}[/]
"""
    console.print(
        Panel(
            menu_text,
            title="[bold green] USER MENU[/]",
            box=ROUNDED,
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


def show_success(message: str):
    console.print(
        Panel(
            message,
            title="[bold green]✓ Muvaffaqiyat[/]",
            box=ROUNDED,
            border_style="bright_green",
        )
    )


def show_error(message: str):
    console.print(
        Panel(
            message,
            title="[bold red]✗ Xato[/]",
            box=ROUNDED,
            border_style="bright_red",
        )
    )


def show_info(message: str):
    console.print(
        Panel(
            message,
            title="[bold cyan] Ma'lumot[/]",
            box=ROUNDED,
            border_style="bright_cyan",
        )
    )


def show_warning(message: str):
    console.print(
        Panel(
            message,
            title="[bold yellow] Ogohlantirish[/]",
            box=ROUNDED,
            border_style="bright_yellow",
        )
    )


def show_products_table(products: list):
    if not products:
        show_info("Hech qanday mahsulot topilmadi")
        return

    table = Table(
        title=" MAHSULOTLAR",
        box=ROUNDED,
        border_style="cyan",
    )

    table.add_column("ID", style="bold yellow", width=5)
    table.add_column("Nomi", style="bold cyan")
    table.add_column("Kategoriya", style="magenta")
    table.add_column("Narx", style="bold green")
    table.add_column("Stock", style="blue")

    for product in products:
        table.add_row(
            str(product.id),
            product.name,
            product.category,
            f"{product.price:,.0f}",
            str(product.stock),
        )

    console.print(table)



def show_cart_table(cart_items: list):
    if not cart_items:
        show_info("Savat bo'sh")
        return

    table = Table(
        title="🛒 SAVAT",
        box=ROUNDED,
        border_style="cyan",
    )

    table.add_column("#", style="bold yellow", width=3)
    table.add_column("Mahsulot", style="bold cyan")
    table.add_column("Miqdor", style="magenta", justify="center")
    table.add_column("Narx", style="bold green")
    table.add_column("Jami", style="bold green")

    total = 0
    for i, item in enumerate(cart_items, 1):
        item_total = item.get_total_price()
        total += item_total
        table.add_row(
            str(i),
            item.product.name,
            str(item.quantity),
            f"{item.product.get_final_price():,.0f}",
            f"{item_total:,.0f}",
        )

    table.add_row("", "", "", "[bold]JAMI:[/]", f"[bold green]{total:,.0f}[/]")
    console.print(table)


def show_orders_table(orders: list):
    if not orders:
        show_info("Hech qanday buyurtma topilmadi")
        return

    table = Table(
        title=" BUYURTMALAR",
        box=ROUNDED,
        border_style="cyan",
    )

    table.add_column("ID", style="bold yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Jami", style="bold green")
    table.add_column("Mahsulot", style="blue")
    table.add_column("Sana", style="yellow")

    for order in orders:
        table.add_row(
            str(order.id),
            order.status,
            f"{order.total_price:,.0f}",
            str(order.get_items_count()),
            order.created_at.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


def show_order_details(order_details: dict):
    if not order_details:
        show_error("Order topilmadi")
        return

    info = f"""
[bold]Order #[/]{order_details['id']}
[bold]Status:[/] {order_details['status']}
[bold]Jami:[/] {order_details['total_price']:,.0f} so'm
[bold]Mahsulotlar:[/] {order_details['items_count']} dona
[bold]Yaratildi:[/] {order_details['created_at'].strftime('%Y-%m-%d %H:%M')}

[bold cyan]Mahsulotlar:[/]
"""

    for item in order_details["items"]:
        info += f"\n • {item['product_name']} x{item['quantity']} = {item['total']:,.0f}"

    console.print(
        Panel(
            info,
            title="[bold green] ORDER DETAILS[/]",
            box=ROUNDED,
            border_style="cyan",
            padding=(1, 2),
        )
    )
