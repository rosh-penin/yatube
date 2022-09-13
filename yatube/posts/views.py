from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    FormView,
    ListView,
    DetailView,
    UpdateView,
    CreateView
)
from django.urls import reverse

from .constants import PAGES
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def get_author(username):
    return get_object_or_404(User, username=username)


class IndexView(ListView):
    """Index page."""
    queryset = Post.objects.select_related('group', 'author')
    template_name = 'posts/index.html'
    paginate_by = PAGES


class GroupView(ListView):
    """Group list page."""
    template_name = 'posts/group_list.html'
    paginate_by = PAGES

    def get_group(self):
        return get_object_or_404(Group, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.get_group()

        return context

    def get_queryset(self):
        group = self.get_group()
        posts = group.posts.select_related('author')

        return posts


class ProfileView(ListView):
    """Profile page."""
    template_name = 'posts/profile.html'
    paginate_by = PAGES

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = get_author(self.kwargs['username'])
        user = self.request.user
        context['author'] = author
        if user.is_authenticated and user != author:
            context['following'] = Follow.objects.filter(
                author=author,
                user=user
            ).exists()

        return context

    def get_queryset(self):
        author = get_author(self.kwargs['username'])
        posts = author.posts.all()

        return posts


class PostDetailView(DetailView):
    """Post detail page."""
    template_name = 'posts/post_detail.html'

    def get_object(self):
        post = get_object_or_404(
            Post.objects.select_related('author', 'group'),
            pk=self.kwargs.get('post_id')
        )

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.get_object().comments.all()
        context['form'] = CommentForm()

        return context


class PostCreateView(LoginRequiredMixin, FormView):
    """Post creating form."""
    template_name = 'posts/post_create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'posts:profile',
            kwargs={'username': self.request.user}
        )

    def form_valid(self, form):
        completed_form = form.save(commit=False)
        completed_form.author = self.request.user
        completed_form.save()

        return super().form_valid(form)


class PostEditView(LoginRequiredMixin, UpdateView):
    """Post editing form."""
    template_name = 'posts/post_create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs.get('post_id'))

    def get_success_url(self):
        return reverse(
            'posts:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True

        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:

            return self.handle_no_permission()

        if request.user != self.get_post().author:
            return redirect(
                'posts:post_detail',
                self.kwargs.get('post_id')
            )

        return super().dispatch(request, *args, **kwargs)


class AddCommentView(LoginRequiredMixin, FormView):
    """Comment adding form. Form is in context on post detail page."""
    http_method_names = ['post']
    form_class = CommentForm

    def form_valid(self, form):
        completed_form = form.save(commit=False)
        completed_form.author = self.request.user
        completed_form.post = get_object_or_404(
            Post,
            pk=self.kwargs.get('post_id')
        )
        completed_form.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'posts:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class FollowIndexView(LoginRequiredMixin, ListView):
    """Posts of followed authors."""
    template_name = 'posts/follow.html'
    paginate_by = PAGES

    def get_queryset(self):
        posts = Post.objects.filter(author__following__user=self.request.user)

        return posts


class ProfileFollowView(LoginRequiredMixin, CreateView):
    """Creating follow table query."""
    def get(self, request, *args, **kwargs):
        author = get_author(self.kwargs['username'])
        user = request.user
        # Is there a way to check this on model level?
        if author != user:
            Follow.objects.get_or_create(author=author, user=user)

        return redirect(
            reverse(
                'posts:profile',
                kwargs={'username': self.kwargs['username']}
            )
        )


class ProfileUnFollowView(LoginRequiredMixin, CreateView):
    """Deleting follow table query."""
    def get(self, request, *args, **kwargs):
        author = get_author(self.kwargs['username'])
        user = request.user
        Follow.objects.filter(author=author, user=user).delete()

        return redirect(
            reverse(
                'posts:profile',
                kwargs={'username': self.kwargs['username']}
            )
        )
