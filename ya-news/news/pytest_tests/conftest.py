from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

import pytest

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Олег')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='НеОлег')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def all_news():
    today = datetime.today()

    news_objects = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]

    News.objects.bulk_create(news_objects)
    return News.objects.all() 

@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def comment_id(comment):
    """Возвращает кортеж с id комментария."""
    return (comment.id,)


@pytest.fixture
def news_id(news):
    """Возвращает кортеж с id новости."""
    return (news.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def detail_url(news_id):
    """Возвращает URL страницы деталей новости."""
    return reverse('news:detail', args=news_id)


@pytest.fixture
def home_url():
    """URL главной страницы."""
    return reverse('news:home')
