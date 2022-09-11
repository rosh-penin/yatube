import shutil

from django.core.cache import cache
from django.urls import reverse
from django.test import override_settings

from posts.models import Post, Group
from posts.constants import PAGES
from .constants import (
    MULTIPLIER_FOR_EVERYTHING,
    TEMP_MEDIA_ROOT
)
from .fixtures import TestBaseWithClients
from .utils import forms_for_test, create_image


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
                )
            )
        Post.objects.bulk_create(generating_list)

    def test_context_and_pages_in_paginator(self):
        """Check pages, number of posts and paginator contex."""
        paginated_context = {
            self.ADDRESS_INDEX: Post.objects.all(),
            self.ADDRESS_GROUP: self.group.posts.all(),
            self.ADDRESS_PROFILE: self.author.posts.all(),
        }
        for address, posts in paginated_context.items():
            if posts.count() % PAGES != 0:
                count_modifier = 1
            count_pages = (posts.count() // PAGES) + count_modifier
            for i in range(1, count_pages + 1):
                response = self.author_client.get(address + f'?page={i}')
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

    def test_context(self):
        """Everything in the right place."""
        context = {
            self.ADDRESS_GROUP: ({'group': ('title', 'pk')}, self.group),
            self.ADDRESS_PROFILE: (
                {'author': ('username', 'pk')},
                self.author,
            ),
            self.ADDRESS_DETAIL: (
                {'post': ('text', 'group', 'author', 'id')},
                self.post
            ),
        }
        for address, (arguments, object_link) in context.items():
            response = self.author_client.get(address)
            for key, fields in arguments.items():
                value = response.context[key]
                for field in fields:
                    with self.subTest(address=address, key=key):
                        self.assertEqual(
                            getattr(value, field),
                            getattr(object_link, field)
                        )

    def test_context_forms(self):
        """Everything in the right place, but for forms."""
        context = (self.ADDRESS_EDIT, self.ADDRESS_CREATE)
        for address in context:
            response = self.author_client.get(address)
            if 'edit' in address:
                with self.subTest(address=address, edit='is edit'):
                    self.assertTrue(response.context['is_edit'])
                    self.assertEqual(response.context['id_post'], self.post.id)
            context_items = forms_for_test(response)
            for key, (object, expected) in context_items.items():
                with self.subTest(name=key):
                    self.assertIsInstance(object, expected)

    def test_new_post(self):
        """Checking new post getting where it should and otherwise."""
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

        context_without_new_post = (self.ADDRESS_GROUP, self.ADDRESS_PROFILE)
        for address in context_without_new_post:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertNotEqual(response.context['page_obj'][0], new_post)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageTests(TestBaseWithClients):
    """New test class for images test with decorator."""
    @classmethod
    def tearDownClass(cls):
        """Delete temp media folder."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_image_in_context(self):
        """
        Create new post with image, checking that image displayed on pages.
        """
        context = (
            self.ADDRESS_INDEX,
            self.ADDRESS_GROUP,
            self.ADDRESS_PROFILE,
        )
        new_post = Post.objects.create(
            text='I wanna see the picture',
            author=self.author,
            group=self.group,
            image=create_image()
        )
        for address in context:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertEqual(
                    response.context['page_obj'][0].image,
                    new_post.image
                )
        address_new_post = reverse(
            self.URL_DETAIL,
            kwargs={'post_id': new_post.pk}
        )
        response = self.author_client.get(address_new_post)
        self.assertEqual(
            response.context['post'],
            new_post
        )


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
    """Test for following."""
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
        response = self.non_author_client.get(self.ADDRESS_PROFILE)
        self.assertFalse(response.context.get('following'))
        response = self.non_author_client.get(self.ADDRESS_FOLLOW, follow=True)
        self.assertTrue(response.context.get('following'))
        response = self.non_author_client.get(
            self.ADDRESS_UNFOLLOW, follow=True
        )
        self.assertFalse(response.context.get('following'))

    def test_new_post_added_to_follow_index(self):
        self.non_author_client.get(self.ADDRESS_FOLLOW, follow=True)
        response_author = self.author_client.get(reverse('posts:follow_index'))
        response_non_author = self.non_author_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response_author.context['page_obj'])
        self.assertIn(self.post, response_non_author.context['page_obj'])
