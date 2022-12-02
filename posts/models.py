from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse


# модель авторов (один к одному)
class Author(models.Model):
    authorRate = models.SmallIntegerField(default=0)
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)

    # функция расчета рейтинга
    def update_rating(self):
        postRat = self.post_set.aaggregate(postRating=Sum('rate'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.aaggregate(commentRating=Sum('rateComment'))
        cRat = 0
        cRat += commentRat.get('commentRating')

        self.authorRate = pRat * 3 + cRat
        self.save()

    def __str__(self):
        return f'{self.authorUser}'


# модель категорий
class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    subscribe = models.ManyToManyField(User, related_name='category')

    def __str__(self):
        return self.name

    # вывод названия модели в админке
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


# модель Сообщений. Делятся на статьи (ARTICLE) и новости(NEWS)
class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    CATEGORIES = [
        (ARTICLE, 'статья'),
        (NEWS, 'новость'),
    ]

    articleType = models.CharField(max_length=2, choices=CATEGORIES, default=NEWS, verbose_name='Тип публикации')
    dateAdd = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    headline = models.CharField(max_length=128, verbose_name='Заголовок')
    text = models.TextField(null=False, verbose_name='Текст статьи')
    picture = models.ImageField(upload_to='images/')
    rate = models.SmallIntegerField(default=0, verbose_name='рейтинг')

    creator = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    postCategory = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.rate += 1
        self.save()
        return self.rate

    def dislike(self):
        self.rate -= 1
        self.save()
        return self.rate

    def preview(self):
        return f'{self.text[:124]} ...'

    def __str__(self):
        return f'{self.headline}. \n' \
               # f'{self.text}\n' - правильное отображение статьи в админке

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'


# связующая модель между материалами и категориями
class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.postThrough.headline

    class Meta:
        verbose_name = 'Выбор категории'
        verbose_name_plural = 'Выбор категории'


# модель комментариев
class Comment(models.Model):
    textComment = models.TextField()
    dateComment = models.DateTimeField(auto_now_add=True)
    rateComment = models.SmallIntegerField(default=0)

    postRel = models.ForeignKey(Post, on_delete=models.CASCADE)
    userRel = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rateComment += 1
        self.save()
        return self.rateComment

    def dislike(self):
        self.rateComment -= 1
        self.save()
        return self.rateComment

    def __str__(self):
        return f'Дата комментария: {self.dateComment}\n' \
               f'{self.textComment}\n' \
               f'рейтинг{self.rateComment}'
