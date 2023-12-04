import pytest

from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Просто текст.',
    )
    return news


@pytest.fixture
def id_news_for_args(news):
    return news.id,


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Просто текст.',
    )
    return comment


@pytest.fixture
def id_comment_for_args(comment):
    return comment.id,


@pytest.fixture
def homepage_news():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def news_commentpage(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок для формы',
        'text': 'Новый текст из формы',
        'slug': 'new-slug'
    }