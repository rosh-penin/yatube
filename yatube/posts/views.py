from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView, DetailView, UpdateView
from django.urls import reverse

from .models import Post, Group, User
from .forms import PostForm, CommentForm


class IndexView(ListView):
    queryset = Post.objects.select_related('group', 'author')
    template_name = 'posts/index.html'
    paginate_by = 10


class GroupView(ListView):
    template_name = 'posts/group_list.html'
    paginate_by = 10

    def get_group(self):
        return get_object_or_404(Group, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.get_group()
        return context

    def get_queryset(self):
        group = self.get_group()
        posts = group.posts.all()
        return posts


class ProfileView(ListView):
    template_name = 'posts/profile.html'
    paginate_by = 10

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.get_author()
        return context

    def get_queryset(self):
        author = self.get_author()
        posts = author.posts.all()
        return posts


class PostDetailView(DetailView):
    template_name = 'posts/post_detail.html'

    def get_object(self):
        post = get_object_or_404(
            Post.objects.select_related('author', 'group'),
            pk=self.kwargs['post_id']
        )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.get_object().comments.all()
        context['form'] = PostForm()
        return context


class PostCreateView(LoginRequiredMixin, FormView):
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
    template_name = 'posts/post_create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_post(self):
        return Post.objects.get(pk=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse(
            'posts:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['id_post'] = self.get_post().pk
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user != self.get_post().author:
            return redirect(
                'posts:post_detail',
                self.kwargs['post_id']
            )

        return super().dispatch(request, *args, **kwargs)


class AddCommentView(LoginRequiredMixin, FormView):
    http_method_names = ['post']
    form_class = CommentForm

    def form_valid(self, form):
        completed_form = form.save(commit=False)
        completed_form.author = self.request.user
        completed_form.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        completed_form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'posts:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
