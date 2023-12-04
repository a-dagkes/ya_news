import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_news_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Анонимному пользователю доступны: главная страница,
    страница отдельной новости, страницы регистрации пользователей,
    входа в учётную запись и выхода из нее.
    """
    url = reverse(name, args=args) if args else reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_comment_for_args')),
        ('news:delete', pytest.lazy_fixture('id_comment_for_args')),
    ),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, args, expected_status
):
    """Страницы удаления и редактирования комментария доступны
    автору комментария. Авторизованному пользователю не доступны
    страницы редактирования и удаления чужих комментариев.
    """
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_comment_for_args')),
        ('news:delete', pytest.lazy_fixture('id_comment_for_args')),
    ),
)
def test_redirects(client, name, args):
    """Анонимному пользователю не доступны страницы редактирования
    и удаления комментариев, при попытке доступа к ним, он перенаправляется
    на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
