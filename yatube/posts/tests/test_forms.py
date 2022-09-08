import shutil

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, User
from .constants import TEMP_MEDIA_ROOT
from .utils import create_image


class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Rock&roll',
            description='nay',
            slug='rock-roll'
        )
        cls.post = Post.objects.create(
            text='i hate testing ' * 15,
            author=cls.author,
            group=cls.group,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_authorized_user_creates_post(self):
        "Авторизованный пользователь может опубликовать пост"
        posts = list(Post.objects.all())
        posts_count_start = Post.objects.count()
        form_data = {
            'text': 'Someone needs a new fish',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        with self.subTest():
            self.assertRedirects(
                response,
                reverse(
                    'posts:profile',
                    kwargs={'username': self.author.username},
                )
            )

        posts = set(Post.objects.all()).difference(posts)
        self.assertEqual(1, len(posts))
        self.assertEqual(Post.objects.count(), posts_count_start + 1)
        posts = posts.pop()

        form_data.update({'author': self.author, 'group': self.group})
        for field, value in form_data.items():
            with self.subTest(name='post correct', field=field):
                self.assertEqual(getattr(posts, field), value)

    def test_edit_post(self):
        """Changing post text and deleting group. Checking."""
        form_data = {}
        form_data['text'] = 'Do i really hate testing?'
        form_data['group'] = ""
        response_post = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
        )
        self.assertRedirects(
            response_post,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.author, self.author)
        self.assertNotEqual(self.group.id, form_data['group'])

    def test_comments(self):
        address = reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk}
        )
        form_data = {
            'text': 'abyrvalg abyrvalgovich chaika',
        }
        with self.subTest(name='AuthorCreatesPost'):
            response = self.author_client.post(
                address,
                data=form_data,
                follow=True
            )
            self.assertEqual(
                response.context['comments'][0].text,
                form_data['text']
            )
        with self.subTest(name='AnonRedirected'):
            response = self.client.post(
                address,
                data=form_data,
            )
            self.assertEqual(
                response.context,
                None
            )
            self.assertRedirects(
                response,
                f'/auth/login/?next={address}'
            )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageTests(TestCase):
    """
    New test class for images test with decorator.
    For forms.
    """
    @classmethod
    def tearDownClass(cls):
        """Delete temp media folder."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_form_with_image(self):
        author = User.objects.create(username='images-user')
        author_client = Client()
        author_client.force_login(author)
        group = Group.objects.create(
            title='ImageGroup',
            description='des',
            slug='group-image'
        )
        image = create_image()
        data_form = {
            'text': 'You live without colors',
            'group': group.pk,
            'image': image
        }
        author_client.post(
            reverse('posts:post_create'),
            data=data_form,
        )
        self.assertTrue(
            Post.objects.filter(image=f'posts/{image}').exists()
        )
