# файл для создания фильтров через запрос (get)
import django_filters
from django.forms import DateInput, TextInput

from .models import Category


# создаем свой набор фильтров по категории сообщений
class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='headline',
        lookup_expr='icontains',
        widget=TextInput(attrs={'type': 'text'}),
        label='Название статьи',
    )

    category = django_filters.ModelChoiceFilter(
        field_name='postCategory',
        queryset=Category.objects.all(),
        label='Категория',
        empty_label='Выбери категорию',
    )

    date_after = django_filters.DateFilter(
        field_name='dateAdd',
        lookup_expr='gt',
        widget=DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date'}, ),
        label='Дата создания',
    )
