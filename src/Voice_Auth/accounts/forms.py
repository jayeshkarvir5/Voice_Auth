# accounts.forms.py
from __future__ import print_function
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from .models import Account, Question
from django.db.models import Q
import speech_recognition as sr
from gtts import gTTS
import os
import random
import time
from google.cloud import translate
from django.utils.translation import ugettext_lazy as _


translate_client = translate.Client()

# For Hindi flag = 1
flag = 1


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Username'))
    answer1 = forms.CharField(label=_('Answer 1'))
    answer2 = forms.CharField(label=_('Answer 2'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        un = kwargs.pop('username', None)
        # print(self.kwargs.get('username'))
        # self.answer1 = bot.getResponse()
        super(UserLoginForm, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        un = self.cleaned_data.get('username')
        try:
            user = Account.objects.get(username=un)
        except Account.DoesNotExist:
            user = None
        print(user)
        if user is None:
            raise forms.ValidationError(_("Invalid Credentials"))
        password = self.cleaned_data.get("password")
        if not user.check_password(password):
                # log auth tries
            raise forms.ValidationError(_("Invalid Credentials"))
        # q1 = self.cleaned_data.get("question1")
        a1 = self.cleaned_data.get("answer1")
        # q2 = self.cleaned_data.get("question2")
        a2 = self.cleaned_data.get("answer2")
        # if user.question1 != q1 or user.question2 != q2:
        # raise forms.ValidationError("Incorrect Question")
        print(a1)
        print(a2)
        if a1 == None or a2 == None:
            raise forms.ValidationError(_("Incorrect response"))
        # Translate to English if Hindi Output
        if flag == 1:
            translation1 = translate_client.translate(a1, target_language='en')
            translation2 = translate_client.translate(a2, target_language='en')
            a1 = translation1['translatedText']
            a2 = translation2['translatedText']
            print("Translated Text: {} {} ".format(a1, a2))

        flag1 = 0
        flag2 = 0
        if user.answer1 in a1:
            flag1 = 1
        if user.answer2 in a2:
            flag2 = 1
        if flag1 != 1 or flag2 != 1:
            raise forms.ValidationError(_("Incorrect response"))
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UsernameForm(forms.Form):
    username = forms.CharField(label=_('Username'))

    def clean_username(self):
        un = self.cleaned_data.get('username')
        print(un)
        qs = Account.objects.filter(username=un)
        print(qs)
        if qs.count() == 0:
            # print(_('Username does not exists'))
            raise forms.ValidationError(_('Username does not exists'))
        return un


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirm password'), widget=forms.PasswordInput)
    # answer1 = forms.CharField(widget=forms.PasswordInput)
    # password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = [
            'email',
            'username',
            'question1',
            'answer1',
            'question2',
            'answer2'
        ]
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'question1': _('Question 1'),
            'question2': _('Question 2'),
            'answer1': _('Answer 1'),
            'answer2': _('Answer 2')
        }
        error_messages: {
            'question1': {
                'required': 'Please let us know what to call you!'
            }
        }

    def __init__(self, username=None, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        un = self.cleaned_data.get('username')
        qs = Account.objects.filter(username=un)
        if qs.exists():
            raise forms.ValidationError(_("Username already exists"))
        return un

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Account.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError(_("Email is taken"))
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password2

    def clean_question2(self):
        q1 = self.cleaned_data.get("question1")
        q2 = self.cleaned_data.get("question2")
        print(q1)
        print(q2)
        if q1.question == q2.question:
            raise forms.ValidationError(_("Please select 2 different questions"))
        return q2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True
        # user.is_active = False
        # create a new user hash for activating email.

        if commit:
            user.save()
        return user
