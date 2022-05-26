from django import template

register = template.Library()


@register.filter
def sum(a, b):
    return a + b


@register.filter
def diff(a, b):
    return a - b


@register.filter
def multiply(a, b):
    return a * b


@register.filter
def ptg(a, b):
    return round((a / b) * 100, 2)
