# Generated by Django 2.2.16 on 2022-09-08 10:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0020_auto_20220908_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='подписчик'),
        ),
    ]
