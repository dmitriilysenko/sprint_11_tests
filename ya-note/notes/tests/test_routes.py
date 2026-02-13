from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='dimasik2')
        cls.reader = User.objects.create(username='stranger')
        cls.note = Note.objects.create(
            title='Заголовок',
            author=cls.author,
            text='Текст заметки'
        )

    def test_anonymous_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:signup',
            'users:logout',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_pages_availability(self):
        urls = (
            'notes:add',
            'notes:list',
            'notes:success',
        )
        self.client.force_login(self.reader)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_the_note_availability(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        urls = ('notes:edit', 'notes:delete', 'notes:detail')

        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        url_config = {
            'notes:edit': True,
            'notes:delete': True,
            'notes:detail': True,
            'notes:add': False,
            'notes:list': False,
            'notes:success': False,
        }
        for name, slug_req in url_config.items():
            with self.subTest(name=name):
                if slug_req:
                    url = reverse(name, args=(self.note.slug,))
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
