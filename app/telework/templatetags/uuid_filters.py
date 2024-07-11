from django import template

register = template.Library()

@register.filter(name='uuid_to_int')
def uuid_to_int(value):
    """
    Convertit un UUID en un entier.
    """
    return int(value)
