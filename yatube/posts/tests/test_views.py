import shutil

from django.core.cache import cache
from django.urls import reverse
from django.test import override_settings

from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, Follow
from posts.constants import PAGES
from .constants import (
    MULTIPLIER_FOR_EVERYTHING,
    TEMP_MEDIA_ROOT
)
from .fixtures import TestBaseWithClients
from .utils import create_image


class TemplateTests(TestBaseWithClients):

    def test_namespace_template_auth(self):
        """Getting template through namespace:name."""
        template_addresses = {
            self.ADDRESS_INDEX: 'posts/index.html',
            self.ADDRESS_GROUP: 'posts/group_list.html',
            self.ADDRESS_PROFILE: 'posts/profile.html',
            self.ADDRESS_DETAIL: 'posts/post_detail.html',
            self.ADDRESS_CREATE: 'posts/post_create.html',
            self.ADDRESS_EDIT: 'posts/post_create.html'
        }
        for address, expected in template_addresses.items():
            with self.subTest(address=address, template=expected):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, expected)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ContextTests(TestBaseWithClients):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        generating_list = []
        for _ in range(MULTIPLIER_FOR_EVERYTHING):
            generating_list.append(
                Post(
                    text='testing is boring ' * MULTIPLIER_FOR_EVERYTHING,
                    author=cls.author,
                    group=cls.group,
                    image=create_image(),
                )
            )
            generating_list.append(
                Post(
                    text='I am not an author',
                    author=cls.non_author,
                    group=cls.group,
                    image=create_image(),
                )
            )
        Post.objects.bulk_create(generating_list)
        Follow.objects.create(author=cls.author, user=cls.non_author)
        cls.follower = cls.non_author.follower.get(author=cls.author)
        cls.fields_page = ('text', 'group', 'author', 'id')

    @classmethod
    def tearDownClass(cls):
        """Delete temp media folder."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def fields_testing(self, context, value, field):
        self.assertEqual(
            getattr(context, field),
            getattr(value, field)
        )

    def test_context_and_pages_in_paginator(self):
        """Check pages, number of posts and querysets of them."""
        paginated_context = {
            self.ADDRESS_INDEX: Post.objects.all(),
            self.ADDRESS_GROUP: self.group.posts.all(),
            self.ADDRESS_PROFILE: self.author.posts.all(),
            self.ADDRESS_PROFOLLOW: self.follower.author.posts.all(),
        }
        for address, posts in paginated_context.items():
            if posts.count() % PAGES != 0:
                count_modifier = 1
            count_pages = (posts.count() // PAGES) + count_modifier
            for i in range(1, count_pages + 1):
                response = self.non_author_client.get(address + f'?page={i}')
                with self.subTest(
                    address=address,
                    page=i,
                ):
                    cut_posts = posts[(PAGES * i - PAGES):(PAGES * i)]
                    self.assertQuerysetEqual(
                        response.context['page_obj'],
                        cut_posts,
                        transform=lambda x: x
                    )

    def test_context_index(self):
        """Everything in the right place. Index."""
        first_post = Post.objects.first()
        response = self.author_client.get(self.ADDRESS_INDEX)
        for field in self.fields_page:
            self.fields_testing(
                response.context['page_obj'][0],
                first_post,
                field,
            )

    def test_context_group(self):
        """Everything in the right place. Group."""
        first_post = self.group.posts.first()
        response = self.author_client.get(self.ADDRESS_GROUP)
        with self.subTest(name='page fields'):
            for field in self.fields_page:
                self.fields_testing(
                    response.context['page_obj'][0],
                    first_post,
                    field
                )
        for field in ('title', 'pk'):
            self.fields_testing(
                response.context['group'],
                self.group,
                field
            )

    def test_context_profile(self):
        """Everything in the right place. Profile."""
        first_post = self.author.posts.first()
        response = self.non_author_client.get(self.ADDRESS_PROFILE)
        with self.subTest(name='page fields'):
            for field in self.fields_page:
                self.fields_testing(
                    response.context['page_obj'][0],
                    first_post,
                    field
                )
        with self.subTest(name='author fields'):
            for field in ('username', 'pk'):
                self.fields_testing(
                    response.context['author'],
                    self.author,
                    field
                )
        self.assertTrue(response.context.get('following'))

    def test_context_detail(self):
        """Everything in the right place. Post detail."""
        response = self.author_client.get(self.ADDRESS_DETAIL)
        for field in ('text', 'group', 'author', 'id'):
            self.fields_testing(
                response.context['post'],
                self.post,
                field
            )
        self.assertIsInstance(
            response.context['form'],
            CommentForm
        )

    def test_context_profollow(self):
        first_post = self.follower.author.posts.first()
        response = self.non_author_client.get(self.ADDRESS_PROFOLLOW)
        for field in self.fields_page:
            self.fields_testing(
                response.context['page_obj'][0],
                first_post,
                field,
            )

    def test_context_forms(self):
        """Everything in the right place, but for forms."""
        addresses = (self.ADDRESS_EDIT, self.ADDRESS_CREATE)
        for address in addresses:
            response = self.author_client.get(address)
            if 'edit' in address:
                with self.subTest(address=address, edit='is edit'):
                    self.assertTrue(response.context['is_edit'])
            with self.subTest(name='form_is_form'):
                self.assertIsInstance(response.context['form'], PostForm)

    def test_new_post(self):
        """Checking new post getting where it should."""
        new_group = Group.objects.create(
            title='This is not the group you are looking for',
            description='cookies for the dark side',
            slug='escape-from-yavin-4',
        )
        new_post = Post.objects.create(
            text='There is a place in the galaxy where the dark side...',
            group=new_group,
            author=self.non_author,
        )
        context_with_new_post = (
            self.ADDRESS_INDEX,
            reverse(
                self.URL_GROUP,
                kwargs={'slug': new_group.slug}
            ),
            reverse(
                self.URL_PROFILE,
                kwargs={'username': self.non_author.username}
            ),
        )
        for address in context_with_new_post:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(response.context['page_obj'][0], new_post)

    def test_new_post_notIn(self):
        """Checking new post NOT getting where it shouldn't."""
        new_group = Group.objects.create(
            title='This is not the group you are looking for',
            description='cookies for the dark side',
            slug='escape-from-yavin-4',
        )
        new_post = Post.objects.create(
            text='There is a place in the galaxy where the dark side...',
            group=new_group,
            author=self.non_author,
        )
        context_without_new_post = (self.ADDRESS_GROUP, self.ADDRESS_PROFILE)
        for address in context_without_new_post:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertNotEqual(response.context['page_obj'][0], new_post)


class CacheTests(TestBaseWithClients):
    """Tests for cache."""
    def test_cached_content_index(self):
        """
        Get response, delete post.
        Get second response, check if responses content are equal.
        Clear cache, get third response.
        Check that third response.content differs.
        """
        response1 = self.author_client.get(self.ADDRESS_INDEX)
        self.post.delete()
        response2 = self.author_client.get(self.ADDRESS_INDEX)
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.author_client.get(self.ADDRESS_INDEX)
        self.assertNotEqual(response1.content, response3.content)


class FollowersTests(TestBaseWithClients):
    """Testcases for following."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ADDRESS_FOLLOW = (
            reverse(
                'posts:profile_follow',
                kwargs=cls.ARG_PROFILE
            )
        )
        cls.ADDRESS_UNFOLLOW = (
            reverse(
                'posts:profile_unfollow',
                kwargs=cls.ARG_PROFILE
            )
        )

    def test_can_follow_and_unfollow(self):
        """Check if user can follow."""
        response = self.non_author_client.get(self.ADDRESS_PROFILE)
        self.assertFalse(response.context.get('following'))
        response = self.non_author_client.get(self.ADDRESS_FOLLOW, follow=True)
        self.assertTrue(response.context.get('following'))

    def test_can_unfollow(self):
        """Check if user can unfollow."""
        Follow.objects.create(author=self.author, user=self.non_author)
        response = self.non_author_client.get(self.ADDRESS_PROFILE)
        self.assertTrue(response.context.get('following'))
        response = self.non_author_client.get(
            self.ADDRESS_UNFOLLOW, follow=True
        )
        self.assertFalse(response.context.get('following'))

    def test_new_post_added_to_follow_index(self):
        """Create new post and check follow_index_page."""
        Follow.objects.create(author=self.author, user=self.non_author)
        new_post = Post.objects.create(
            text='asdasdasd',
            author=self.author,
        )
        response = self.non_author_client.get(reverse('posts:follow_index'))
        self.assertIn(new_post, response.context['page_obj'])

    def test_new_post_not_added_to_follow_index(self):
        """Create new post and check follow_index_page."""
        Follow.objects.create(author=self.author, user=self.non_author)
        new_post = Post.objects.create(
            text='asdasdasd',
            author=self.author,
        )
        response_author = self.author_client.get(reverse('posts:follow_index'))
        self.assertNotIn(new_post, response_author.context['page_obj'])
