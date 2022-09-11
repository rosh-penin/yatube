import shutil

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, User, Comment
from .constants import TEMP_MEDIA_ROOT
from .utils import create_image


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTest(TestCase):
    """Testing various forms."""
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
        cls.image = create_image()

    @classmethod
    def tearDownClass(cls):
        """Delete temp media folder."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_authorized_user_creates_post(self):
        "Авторизованный пользователь может опубликовать пост"
        posts = Post.objects.all()
        posts_count_start = posts.count()
        posts_initial = list(posts)
        form_data = {
            'text': 'Someone needs a new fish',
            'group': self.group.id,
            'image': self.image
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

        posts = set(Post.objects.all()).difference(posts_initial)
        self.assertEqual(1, len(posts))
        self.assertEqual(Post.objects.count(), posts_count_start + 1)
        posts = posts.pop()

        form_data.update({'author': self.author, 'group': self.group})
        for field, value in form_data.items():
            if field == 'image':
                value = f'posts/{value}'
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
        self.assertNotEqual(self.post.group, self.group)

    def test_comment_create(self):
        """Authorized can create new comment, anon redirected to login."""
        comments = Comment.objects.all()
        comments_count = comments.count()
        comments_initial = list(comments)
        address = reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.pk}
        )
        form_data = {
            'text': 'abyrvalg abyrvalgovich chaika',
        }
        with self.subTest(name='AuthorCreatesComment'):
            response = self.author_client.post(
                address,
                data=form_data,
                follow=True
            )
            comments = set(Comment.objects.all()).difference(comments_initial)
            self.assertEqual(1, len(comments))
            self.assertEqual(Comment.objects.count(), comments_count + 1)

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
