import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(client, homepage_news):
    """На главной странице не более 10 новостей."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, homepage_news):
    """Новости отсортированы от новых к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(id_comment_for_args, client, news_commentpage):
    """Комментарии отсортированы от старых к новым."""
    url = reverse('news:detail', args=id_comment_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_content',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_pages_contains_form(
    parametrized_client,
    form_in_content,
    id_news_for_args
):
    """Авторизованному пользователю доступна форма для отправки комментария.
    Для анонимного пользователя форма недоступна.
    """
    url = reverse('news:detail', args=id_news_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_content
