from django.test import Client, TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class UrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.context = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def setUp(self):
        user = User.objects.create(username='auth')
        self.guest_client = Client()
        self.user_client = Client()
        self.user_client.force_login(user)

    def test_templates_for_authorized_user(self):
        context = UrlTests.context
        for address, template in context.items():
            with self.subTest(name='template_test_auth', address=address):
                response = self.user_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_templates_for_anonymous(self):
        context = UrlTests.context
        for address, template in context.items():
            with self.subTest(name='template_test_anon', address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
