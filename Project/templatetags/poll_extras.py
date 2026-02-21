from django import template

register = template.Library()


@register.filter
def get(d, key):
    """Доступ к значению словаря по ключу в шаблоне: {{ poll_stats|get:task.id }}"""
    try:
        if d is None or not hasattr(d, 'get') or not callable(getattr(d, 'get')):
            return None
        # Ключи в poll_stats — int; в шаблоне key может прийти строкой
        result = d.get(key)
        if result is not None:
            return result
        if key is not None:
            try:
                return d.get(int(key))
            except (TypeError, ValueError):
                pass
    except (TypeError, AttributeError):
        pass
    return None
