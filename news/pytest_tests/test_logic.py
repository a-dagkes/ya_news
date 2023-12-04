import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from pytils.translit import slugify

from django.contrib.auth import get_user
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING

from news.models import Comment, News


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, id_news_for_args, form_data):
    url = reverse('news:detail', args=id_news_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_auth_user_can_create_comment(author_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == get_user(author_client)


def test_user_cant_use_bad_words(author_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0



def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    news_url = reverse('news:detail', args=(comment.news.id,))
    assertRedirects(response, f'{news_url}#comments')
    # assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0

def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, comment, form_data):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    news_url = reverse('news:detail', args=(comment.news.id,))
    assertRedirects(response, f'{news_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, form_data
):
    original_text = comment.text
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
