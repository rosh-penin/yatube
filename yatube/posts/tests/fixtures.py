from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


class TestBase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.non_author = User.objects.create_user(username='htua')
        cls.group = Group.objects.create(
            title="TestingGroup",
            slug="test-slug",
            description="ihatetesting",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="S" * 100,
            group=cls.group,
        )


class TestBaseWithClients(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.non_author_client = Client()
        cls.non_author_client.force_login(cls.non_author)
        cls.URL_INDEX = 'posts:index'
        cls.URL_GROUP = 'posts:group_list'
        cls.ARG_GROUP = {'slug': cls.group.slug}
        cls.URL_PROFILE = 'posts:profile'
        cls.ARG_PROFILE = {'username': cls.author.username}
        cls.URL_DETAIL = 'posts:post_detail'
        cls.ARG_DETAIL = {'post_id': cls.post.pk}
        cls.URL_CREATE = 'posts:post_create'
        cls.URL_EDIT = 'posts:post_edit'
        cls.ARG_EDIT = {'post_id': cls.post.pk}
        cls.URL_PROFOLLOW = 'posts:follow_index'
        cls.ADDRESS_INDEX = reverse(cls.URL_INDEX)
        cls.ADDRESS_GROUP = reverse(cls.URL_GROUP, kwargs=cls.ARG_GROUP)
        cls.ADDRESS_PROFILE = reverse(cls.URL_PROFILE, kwargs=cls.ARG_PROFILE)
        cls.ADDRESS_DETAIL = reverse(cls.URL_DETAIL, kwargs=cls.ARG_DETAIL)
        cls.ADDRESS_CREATE = reverse(cls.URL_CREATE)
        cls.ADDRESS_EDIT = reverse(cls.URL_EDIT, kwargs=cls.ARG_EDIT)
        cls.ADDRESS_PROFOLLOW = reverse(cls.URL_PROFOLLOW)
