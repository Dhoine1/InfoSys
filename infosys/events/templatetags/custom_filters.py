from django import template


register = template.Library()


@register.filter()
def rename(value):
    new_t = value.replace('этаж', 'floor')
    
    return f'{new_t}'

