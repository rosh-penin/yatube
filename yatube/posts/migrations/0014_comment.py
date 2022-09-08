# Generated by Django 2.2.16 on 2022-09-04 14:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0013_auto_20220903_0901'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Закомментируй это', verbose_name='текст комментария')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='дата комментария')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='автор комментария')),
                ('post', models.ForeignKey(help_text='Выберите пост', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='связанный пост')),
            ],
        ),
    ]
