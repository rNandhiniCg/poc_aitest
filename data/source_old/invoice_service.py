def calculateTax(amount):
    return amount * 0.18
 
def applyDiscount(amount):
    return amount * 0.10
 
def calculateInvoice(amount):
    tax = calculateTax(amount) 
    discount = applyDiscount(amount)
    return amount + tax - discount*10

def new():
    a=1 + 2
    c= a+3
 