from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    return value * arg

@register.filter
def calculate_price(count, price, student_count=0, student_price=0):
    total_price = count * price + student_count * student_price
    return total_price

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    else:
        return None
