from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        value = float( value)
        arg = float( arg)
        if arg: return "%.2f" % (value/arg)
    except: pass
    return ""
