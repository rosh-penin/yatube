from django.contrib import admin

from .models import Post, Group, Follow


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Config for Group Model in admin panel.
    """
    list_display = (
        'pk',
        'title',
        'description',
        'slug',
    )
    search_fields = ('title', 'description')
    list_filter = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Config for Post Model in admin panel.
    """
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    I dont know what i'm doing anymore.
    """
    list_display = (
        'pk',
        'author',
    )
