from django import template
import json

register = template.Library()

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except Exception:
        return ''
    
@register.filter
def json_pretty(value):
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except Exception:
        return str(value)
