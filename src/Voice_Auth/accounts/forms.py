# accounts.forms.py
from __future__ import print_function
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from .models import Account, Question, Generalq
from django.db.models import Q
import os
import random
import time
from Voice_Auth import settings
from google.cloud import translate
from django.utils.translation import ugettext_lazy as _
from accounts.test_speaker import identify_speaker
from accounts.train_model import createGMM

translate_client = translate.Client()

# For Hindi flag = 1
flag = 1


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Username'))
    answer1 = forms.CharField(label=_('Answer 1'))
    answer2 = forms.CharField(label=_('Answer 2'))
    answer3 = forms.CharField(label=_('Answer 3'))
    answer4 = forms.CharField(label=_('Answer 4'))
    password = forms.CharField(label=_('Pass Phrase'), widget=forms.PasswordInput)
    gq1 = forms.CharField(widget=forms.HiddenInput)
    gq2 = forms.CharField(widget=forms.HiddenInput)

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
        a1 = self.cleaned_data.get("answer1")
        a2 = self.cleaned_data.get("answer2")
        a3 = self.cleaned_data.get("answer3")
        a4 = self.cleaned_data.get("answer4")
        gq1 = self.cleaned_data.get("gq1")
        gq2 = self.cleaned_data.get("gq2")
        q3 = Generalq.objects.get(pk=gq1)
        q4 = Generalq.objects.get(pk=gq2)
        # gqans1 = Generalq.objects.get(pk=gq1)
        # if user.question1 != q1 or user.question2 != q2:
        # raise forms.ValidationError("Incorrect Question")
        print(q3.answer)
        print(q4.answer)
        if a1 == None or a2 == None or a3 == None or a4 == None:
            raise forms.ValidationError(_("Incorrect response"))

        out = open(settings.MEDIA_ROOT + "/test_set.txt", "w")
        out.write(un + '-\\a1.wav\n')
        out.write(un + '-\\a2.wav\n')
        out.write(un + '-\\a3.wav\n')
        out.write(un + '-\\a4.wav\n')
        out.write(un + '-\\a5.wav\n')
        out.write(un + '-\\a6.wav\n')
        out.write(un + '-\\a7.wav\n')
        out.close()

        res = identify_speaker(un)
        print("Speaker: {} {}".format(res, un))
        if res == un:
            print('Voice Matched')
        elif res == 'ga2020':
            raise forms.ValidationError(_("User is probably not a human. Please try again"))
        else:
            raise forms.ValidationError(_("Incorrect Voice Signature"))
        # Translate to English if Hindi Output
        if flag == 1:
            translation1 = translate_client.translate(a1, target_language='en')
            translation2 = translate_client.translate(a2, target_language='en')
            # a1 = translation1['translatedText']
            # a2 = translation2['translatedText']
            print("Translated Text: {} {} ".format(a1, a2))

        flag1 = 0
        flag2 = 0
        flag3 = 0
        flag4 = 0
        if user.answer1 in a1:
            flag1 = 1
        if user.answer2 in a2:
            flag2 = 1
        a3 = a3.lower()
        a4 = a4.lower()
        if q3.answer in a3:
            flag3 = 1
        if q4.answer in a4:
            flag4 = 1
        if flag1 != 1 or flag2 != 1 or flag3 != 1 or flag4 != 1:
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
    password1 = forms.CharField(label=_('Pass Phrase'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirm Pass Phrase'), widget=forms.PasswordInput)
    # password = forms.CharField(widget=forms.PasswordInput)
    paragraph = _('Paragraph')
    s1_label = _('Sentence 1')
    s2_label = _('Sentence 2')
    s3_label = _('Sentence 3')
    
    s1 = _('What joy there is in living.')
    s2 = _('The bark of the tree was shiny and dark.')
    s3 = _('A king ruled the state in the early days.')
    
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
            'answer2': _('Answer 2'),
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
            raise forms.ValidationError(_("Pass Phrases don't match"))
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
        un = user.username
        out = open(settings.MEDIA_ROOT + "/dev_set.txt", "w")
        out.write(un + '-\\a1.wav\n')
        out.write(un + '-\\a2.wav\n')
        out.write(un + '-\\a3.wav\n')
        out.write(un + '-\\a4.wav\n')
        out.write(un + '-\\a5.wav\n')

        createGMM(un)
        if commit:
            user.save()

        return user
