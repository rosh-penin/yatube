# Generated by Django 2.2.16 on 2022-09-06 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20220905_0522'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
    ]
