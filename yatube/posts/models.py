from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel

from .constants import CUT_STR_POST


User = get_user_model()


class Group(models.Model):
    """
    Group model for groups with unique url.
    """
    title = models.CharField('название группы', max_length=200)
    slug = models.SlugField(
        'адрес группы',
        unique=True,
    )
    description = models.TextField('описание группы', max_length=500)

    def __str__(self):
        return self.title


class Post(CreatedModel):
    """
    Posts. Main thing this project is about.
    """
    text = models.TextField(
        'текст поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор поста',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='группа поста',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        'Picture',
        upload_to='posts/',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:CUT_STR_POST]


class Comment(CreatedModel):
    """Comments to the posts."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='связанный пост',
        help_text='Выберите пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор комментария',
    )
    text = models.TextField(
        'текст комментария',
        help_text='Закомментируй это',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    # Я все еще считаю что OneToOne и ManyToMany тут смотрелись бы лучше.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='писака',
    )
