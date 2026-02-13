from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    TEST_SLUG = 'test-slug'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Олег')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.TEST_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        login_url = reverse('users:login')
        response = self.client.post(self.url, data=self.form_data)
        redirect_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.author, self.user)

    def test_slug_is_original(self):
        Note.objects.create(
            title='Другой заголовок',
            text='Другой текст',
            author=self.user,
            slug=self.TEST_SLUG
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.TEST_SLUG + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_slug_is_slugify(self):
        form_data = {
            'title': 'Слагифай-специфичный заголовок',
            'text': 'Слагифай-специфичный текст',
        }
        response = self.auth_client.post(self.url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        expected_slug = slugify(form_data['title'])[:100]
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(TestCase):

    NOTE_TITILE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст'
    SUCCESS_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Олег')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.stranger = User.objects.create(username='неОлег')
        cls.stranger_client = Client()
        cls.stranger_client.force_login(cls.stranger)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITILE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_upd_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.stranger_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(
            self.edit_url,
            data=self.form_upd_data
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.stranger_client.post(
            self.edit_url,
            data=self.form_upd_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
