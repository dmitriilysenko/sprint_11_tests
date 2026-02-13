from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects, assertFormError
import pytest


from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(
        author_client, author, form_data, news, detail_url):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    form = response.context['form']
    assertFormError(
        form=form,
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment_id, detail_url):
    delete_url = reverse('news:delete', args=comment_id)
    url_to_comments = detail_url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_id):
    delete_url = reverse('news:delete', args=comment_id)
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client, comment_id, detail_url, form_data, comment):
    edit_url = reverse('news:edit', args=comment_id)
    response = author_client.post(edit_url, data=form_data)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client, form_data, comment_id, comment):
    initial_text = comment.text
    edit_url = reverse('news:edit', args=comment_id)
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == initial_text
