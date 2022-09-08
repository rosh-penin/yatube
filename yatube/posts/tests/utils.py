from django import forms

from django.core.files.uploadedfile import SimpleUploadedFile


def forms_for_test(response):
    """Creates dict for use in the test."""
    return {
        'text': (
            response.context.get('form').fields.get('text'),
            forms.fields.CharField
        ),
        'group': (
            response.context.get('form').fields.get('group'),
            forms.fields.ChoiceField
        ),
        'image': (
            response.context.get('form').fields.get('image'),
            forms.fields.ImageField
        ),
    }


def create_image():
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )
    uploaded = SimpleUploadedFile(
        name='small.gif',
        content=small_gif,
        content_type='image/gif'
    )
    return uploaded
