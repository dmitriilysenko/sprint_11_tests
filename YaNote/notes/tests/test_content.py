from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пупсик')
        cls.reader = User.objects.create(username='stranger')
        notes = []
        for index in range(5):
            notes.append(
                Note(
                    title=f'Тестовая заметка {index + 1}',
                    text='Просто текст заметки.',
                    author=cls.author,
                    slug=f'slug-{index + 1}',
                )
            )
        Note.objects.bulk_create(notes)

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        notes_in_context = response.context['object_list']
        list_ids = [note.id for note in notes_in_context]
        sorted_ids = sorted(list_ids)
        self.assertEqual(
            list_ids, sorted_ids,
            'Заметки должны быть отсортированы по id (от меньшего к большему)'
        )

    def test_notes_in_list(self):
        users_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        author_notes = Note.objects.filter(author=self.author)
        for user, should_see in users_statuses:
            self.client.force_login(user)
            response = self.client.get(url)
            notes_in_context = response.context['object_list']
            for note in author_notes:
                if should_see:
                    self.assertIn(note, notes_in_context)
                else:
                    self.assertNotIn(note, notes_in_context)
            if should_see:
                self.assertEqual(
                    notes_in_context.count(),
                    author_notes.count()
                )
            else:
                self.assertEqual(notes_in_context.count(), 0)

    def test_pages_contains_form(self):
        urls = {
            'notes:add': False,
            'notes:edit': True,
        }
        self.client.force_login(self.author)
        note = Note.objects.filter(author=self.author).first()
        for name, slug_req in urls.items():
            with self.subTest(name=name):
                if slug_req:
                    url = reverse(name, args=(note.slug,))
                else:
                    url = reverse(name)
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
