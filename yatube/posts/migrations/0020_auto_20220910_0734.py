# Generated by Django 2.2.16 on 2022-09-10 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0019_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Напиши сюда', verbose_name='Текст'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Напиши сюда', verbose_name='Текст'),
        ),
    ]
