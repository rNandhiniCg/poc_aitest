import pytest
from source_code.store import (
    Product,
    Order,
    InventoryService,
    PaymentService,
    OrderService,
    OutOfStockError,
    PaymentFailedError,
)

# ---------- Models ----------

def test_product_init_and_repr():
    p = Product(1, "Laptop", 1299.99)
    assert p.product_id == 1
    assert p.name == "Laptop"
    assert p.price == 1299.99
    assert "<Product 1: Laptop ($1299.99)>" in repr(p)

def test_product_negative_price():
    with pytest.raises(ValueError):
        Product(2, "Phone", -10)

def test_order_total_amount():
    p1 = Product(1, "A", 10)
    p2 = Product(2, "B", 5.5)
    o = Order(100, [p1, p2])
    assert o.total_amount == 15.5

# ---------- Inventory ----------

def test_inventory_add_and_reduce_stock():
    inv = InventoryService()
    inv.add_stock(1, 5)
    assert inv.get_available(1) == 5

    inv.reduce_stock(1, 2)
    assert inv.get_available(1) == 3

def test_inventory_out_of_stock_error():
    inv = InventoryService()
    inv.add_stock(1, 1)
    with pytest.raises(OutOfStockError):
        inv.reduce_stock(1, 2)

def test_inventory_invalid_qty():
    inv = InventoryService()
    with pytest.raises(ValueError):
        inv.add_stock(1, 0)
    inv.add_stock(1, 3)
    with pytest.raises(ValueError):
        inv.reduce_stock(1, 0)

# ---------- Payment ----------

def test_payment_success():
    pay = PaymentService()
    assert pay.process_payment(100.0, "1234567") is True

def test_payment_invalid_card():
    pay = PaymentService()
    with pytest.raises(PaymentFailedError):
        pay.process_payment(50, "abc123")  # non-digit

def test_payment_declined_card():
    pay = PaymentService()
    with pytest.raises(PaymentFailedError):
        pay.process_payment(50, "7777770")  # ends with 0

def test_payment_zero_amount():
    pay = PaymentService()
    with pytest.raises(PaymentFailedError):
        pay.process_payment(0, "12345")

# ---------- Order Service ----------

def setup_services():
    inv = InventoryService()
    pay = PaymentService()
    svc = OrderService(inv, pay)
    return inv, pay, svc

def test_order_success_flow():
    inv, pay, svc = setup_services()
    p = Product(1, "Headphones", 199.0)
    inv.add_stock(1, 2)

    order = svc.create_order([p], "9876543")
    assert order.order_id == 1
    assert order.total_amount == 199.0
    assert inv.get_available(1) == 1  # deducted

def test_order_fails_on_out_of_stock():
    inv, pay, svc = setup_services()
    p = Product(1, "Monitor", 300.0)
    # no stock added
    with pytest.raises(OutOfStockError):
        svc.create_order([p], "9876543")

def test_order_fails_on_payment():
    inv, pay, svc = setup_services()
    p = Product(1, "Keyboard", 75.0)
    inv.add_stock(1, 1)
    with pytest.raises(PaymentFailedError):
        svc.create_order([p], "123450")  # ends with 0 → decline

def test_cannot_create_empty_order():
    inv, pay, svc = setup_services()
    with pytest.raises(ValueError):
        svc.create_order([], "12345")