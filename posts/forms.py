from django.forms import ModelForm
from .models import Post


class NewsForm(ModelForm):
    class Meta:
        model = Post
        fields = [
            'headline',
            'text',
            'creator',
            'postCategory',
        ]


class ArticleForm(ModelForm):
    class Meta:
        model = Post
        fields = [
            'headline',
            'text',
            'creator'
        ]
