from django.test import Client, TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class UrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.context = {
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            # '/auth/reset/<uidb64>/<token>/':
            # 'users/password_reset_confirm.html',
            # dont know how to test this
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/contact/': 'users/contact.html',
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
                if address in (
                    '/auth/password_change/',
                    '/auth/password_change/done/'
                ):
                    self.assertRedirects(
                        response,
                        f'/auth/login/?next={address}'
                    )
                    continue

                self.assertTemplateUsed(response, template)
