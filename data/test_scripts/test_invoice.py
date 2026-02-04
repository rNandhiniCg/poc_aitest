from source_code.invoice_service import calculateInvoice,applyDiscount,calculateTax

def test_TC_01_calculate_invoice():
    """Verify invoice calculation with tax"""
    result = calculateInvoice(100)
    assert result > 0
 
def test_TC_02_apply_discount():
    """Verify discount logic"""
    result = applyDiscount(100)
    assert result > 0

def test_TC_03_calculate_tax():
    "Verify calculateTax"
    result = calculateTax(400)
    assert result >0
