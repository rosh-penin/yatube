import shutil
from http import HTTPStatus

from django.test import override_settings

from .constants import TEMP_MEDIA_ROOT
from .fixtures import TestBaseWithClients


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UrlTests(TestBaseWithClients):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.urls_of_templates = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/post_create.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
        }

    @classmethod
    def tearDownClass(cls):
        """Delete temp media folder."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_url_access_with_templates_for_authorized_user(self):
        for address, template in self.urls_of_templates.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_access_with_templates_for_anonymous(self):
        for address, template in self.urls_of_templates.items():
            if address in ('/create/', f'/posts/{self.post.id}/edit/'):
                with self.subTest(address=address, name='Refuse anon'):
                    response = self.client.get(address)
                    self.assertTemplateNotUsed(response, template)
                    continue

            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_redirects(self):
        for address in ('/create/', f'/posts/{self.post.pk}/edit/'):
            with self.subTest(name='anon redirect', address=address):
                response = self.client.get(address)
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={address}'
                )
        with self.subTest(
            name='non-author edit redirect',
            address=f'/posts/{self.post.pk}/edit/'
        ):
            response = self.non_author_client.get(
                f'/posts/{self.post.pk}/edit/',
                follow=True
            )
            self.assertRedirects(
                response,
                f'/posts/{self.post.pk}/'
            )

    def test_404(self):
        response = self.author_client.get('/posts/chupakabra/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
