from datetime import datetime

from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives

from .models import Category

from .filters import PostFilter
from .forms import *


# def make_news(sender, instance, created, **kwargs):
#     html_content = render_to_string(
#         'news_email',
#         {'news': post_save}
#     )
#     subscribers = Category.objects.filter(subscribe=True)
#
#     msg = EmailMultiAlternatives(
#         subject=f'Новая статья: {post_save.headline}',
#         body=post_save,
#         from_email='',
#         to=self.request.user in self.postCategory.subscribe.all()
#     )


class PostsLIst(ListView):
    model = Post  # какую модель используем
    ordering = '-dateAdd'  # по какому полю пойдет сортировка
    template_name = 'articles.html'  # шаблон для отображения
    context_object_name = 'posts'  # список объектов, которые будут передаваться в шаблон
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        # обращаемся к родительскому классу
        # и вызываем этот же метод с теми же аргументами,
        # что были переданы нам.
        context = super().get_context_data(**kwargs)
        # К словарю добавляем текущую дату с ключом 'time_now'
        context['time_now'] = datetime.utcnow()  # создаем переменную time_now
        context['filterset'] = self.filterset  # создаем переменную filterset с данным из запроса
        return context


class SearchLIst(ListView):
    model = Post  # какую модель используем
    ordering = '-dateAdd'  # по какому полю пойдет сортировка
    template_name = 'search.html'  # шаблон для отображения
    context_object_name = 'posts'  # список объектов, которые будут передаваться в шаблон
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        # обращаемся к родительскому классу
        # и вызываем этот же метод с теми же аргументами,
        # что были переданы нам.
        context = super().get_context_data(**kwargs)
        # К словарю добавляем текущую дату с ключом 'time_now'
        context['time_now'] = datetime.utcnow()  # создаем переменную time_now
        context['filterset'] = self.filterset  # создаем переменную filterset с данным из запроса
        return context


class PostsDetails(DetailView):
    model = Post
    ordering = 'dateAdd'
    template_name = 'post.html'
    context_object_name = 'post'


# Создаем представление для отображения страницы создания новости
class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('post.add_news',)
    form_class = NewsForm
    model = Post
    template_name = 'news_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.articleType = 'NW'

        html_content = render_to_string('news_email.html',
                                        {
                                            'post': post,
                                        })
        msg = EmailMultiAlternatives(
            subject=f'{post.title}',
            body=post.text,
            from_email='tandrin.mail@yandex.ru',
            to=['kudashova@inbox.ru']
        )

        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return super().form_valid(form)


# Создаем представление для отображения страницы модерации новости
class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('post.change_news',)

    form_class = NewsForm
    model = Post
    template_name = 'news_update.html'


# Создаем представление для отображения страницы удаления новости
class NewsDel(PermissionRequiredMixin, DeleteView):
    permission_required = ('post.delete_news',)

    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('post_list')


# Создаем представление для отображения страницы создания статьи
class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('post.add_article',)

    form_class = ArticleForm
    model = Post
    template_name = 'art_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.articleType = 'AR'
        return super().form_valid(form)


class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('post.change_article',)
    form_class = ArticleForm
    model = Post
    template_name = 'art_update.html'


class ArticleDel(PermissionRequiredMixin, DeleteView):
    permission_required = ('post.delete_article',)
    model = Post
    template_name = 'art_delete.html'
    success_url = reverse_lazy('post_list')


class CategoryView(ListView):
    model = Post  # какую модель используем
    ordering = '-dateAdd'  # по какому полю пойдет сортировка
    template_name = 'category_list.html'  # шаблон для отображения
    context_object_name = 'category_news'  # список объектов, которые будут передаваться в шаблон
    paginate_by = 5

    def get_queryset(self):
        self.postCategory = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(postCategory=self.postCategory).order_by('-dateAdd')
        return queryset

    def get_context_data(self, **kwargs):
        # обращаемся к родительскому классу
        # и вызываем этот же метод с теми же аргументами, что были переданы нам.
        context = super().get_context_data(**kwargs)
        # К словарю добавляем переменные

        context['is_not_subscriber'] = self.request.user not in self.postCategory.subscribe.all()
        context['Category'] = self.postCategory
        return context
