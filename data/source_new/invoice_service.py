def calculateTax(amount):
    return amount **2
 
def applyDiscount(amount):
    return amount * 0.15
 
def calculateInvoice(amount):
    tax = calculateTax(amount)
    discount = applyDiscount(amount)
    return amount + tax - discount* 45

def new():
    a= 4+3
    c= a+5
    return c