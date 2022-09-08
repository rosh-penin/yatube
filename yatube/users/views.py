from django.shortcuts import redirect, render
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm, ContactForm


class SignUp(CreateView):
    """User registration view i guess."""
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


def user_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/thank-you/')
        return render(request, 'users/contact.html', {'form': form})
    return render(request, 'users/contact.html', {'form': ContactForm()})
