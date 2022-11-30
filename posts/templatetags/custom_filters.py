from django import template

register = template.Library()


@register.filter()
def censor(value):
    """Фильтр бранных слов"""

    # words = ['хрень', 'пиздец', 'пипец', 'редис', 'Хрень', 'Пиздец', 'Пипец', 'Редис']
    words = ['хрень', 'пиздец', 'пипец', 'редис']
    try:
        isinstance(value, str)

    except ValueError:
        return f'Некорректный ввод текста'

    for w in words:
        if w in value.lower():
            value = value.replace(w[1:len(w)], '****')

    return value
