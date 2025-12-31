from django import template

register = template.Library()
print("DEBUG: math_filters loaded!")

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def currency_cfa(value):
    """Format currency in CFA."""
    try:
        return f"{float(value):,.0f} CFA"
    except (ValueError, TypeError):
        return "0 CFA"