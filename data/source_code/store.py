# ============================
# MODELS
# ============================

class Product:
    def __init__(self, product_id: int, name: str, price: float):
        if price < 0:
            raise ValueError("price cannot be negative")
        self.product_id = product_id
        self.name = name
        self.price = float(price)

    def __repr__(self):
        return f"<Product {self.product_id}: {self.name} (${self.price:.2f})>"


class Order:
    def __init__(self, order_id: int, products: list):
        self.order_id = order_id
        self.products = list(products or [])

    @property
    def total_amount(self) -> float:
        return sum(p.price for p in self.products)


# ============================
# EXCEPTIONS
# ============================

class OutOfStockError(Exception):
    """Raised when requested quantity exceeds available stock."""
    pass


class PaymentFailedError(Exception):
    """Raised when payment gateway declines the transaction."""
    pass


# ============================
# SERVICES
# ============================

class InventoryService:
    """
    A simple in-memory inventory.
    stock: dict[product_id, available_qty]
    """
    def __init__(self):
        self.stock = {}

    def add_stock(self, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        self.stock[product_id] = self.stock.get(product_id, 0) + qty

    def reduce_stock(self, product_id: int, qty: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        available = self.stock.get(product_id, 0)
        if available < qty:
            raise OutOfStockError(f"Product {product_id} is out of stock. Need {qty}, have {available}")
        self.stock[product_id] = available - qty

    def get_available(self, product_id: int) -> int:
        return self.stock.get(product_id, 0)


class PaymentService:
    """
    Fake payment rules:
      - Any card number ending with '0' fails.
      - Amount must be > 0.
    """
    def process_payment(self, amount: float, card_number: str) -> bool:
        if amount <= 0:
            raise PaymentFailedError("Amount must be greater than zero.")
        if not card_number or not card_number.isdigit():
            raise PaymentFailedError("Invalid card details.")
        if card_number.endswith("0"):
            raise PaymentFailedError("Payment failed: card declined.")
        return True
    
class OrderService:
    def __init__(self, inventory_service, payment_service):
        self.inventory = inventory_service
        self.payment = payment_service
        self.order_counter = 1

    def create_order(self, products, card_number):
        # Check inventory
        for p in products:
            self.inventory.reduce_stock(p.product_id, 1)

        # Calculate amount
        order = Order(self.order_counter, products)
        amount = order.total_amount

        # Take payment
        self.payment.process_payment(amount, card_number)

        # Success
        self.order_counter += 1
        return order
