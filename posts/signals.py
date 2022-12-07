from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from NA_project import settings
from posts.models import PostCategory


def make_news(preview, pk, headline, subscribe, categories):
    html_content = render_to_string(
        'news_email.html',
        {'text': preview,
         'link': f'{settings.SITE_URL}/posts/{pk}',
         'categories': categories,
         }
    )

    msg = EmailMultiAlternatives(
        subject=f'Новая статья: {headline}',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribe,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@receiver(m2m_changed, sender=PostCategory)
def signal_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.postCategory.all()
        subscribers: list[str] = []
        for cat in categories:
            subscribers += cat.subscribe.all()

        subscribers = [s.email for s in subscribers]

        make_news(instance.preview(), instance.pk, instance.headline, subscribers, categories)
