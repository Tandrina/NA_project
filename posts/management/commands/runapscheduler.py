import datetime
import logging

from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from posts.models import Post, Category

logger = logging.getLogger(__name__)


# мое будущее приложение по рассылке
def my_job():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    post = Post.objects.filter(dateAdd__gte=last_week)
    categories = set(post.values_list('postCategory__name', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list('subscribe__email', flat=True))

    html_content = render_to_string(
        'weekly_post.html',
        {
            'list': settings.SITE_URL,
            'posts': post
        }
    )

    msg = EmailMultiAlternatives(
        subject='Новые статьи',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


# Функция, которая будет удалять неактуальные задачи
def delete_old_job_execution(max_age=604_800):
    """This job delete all apscheduler job executions older than `max_age` from the database"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = 'Runs apscheduler.'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем задачу в таски
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon"),
            id='my_job',
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        # каждую неделю будут удаляться старые задачи, которые  или уже не выполнить, или выполнять не нужно.
        scheduler.add_job(
            delete_old_job_execution,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_execution",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_execution'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
