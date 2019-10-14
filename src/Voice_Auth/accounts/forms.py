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


class ResponseBot:

    def __init__(self):
        print('Bot Created')

    def askQuestion(self, questions):
        index = random.randint(1, 5)
        print(questions[index])
        return index

    def verifyResponse(self, answers, response, index):
        for i in answers[index]:
            if i in response:
                return True
        return False

    def getResponse(self):
        r = sr.Recognizer()
#         print(sr.Microphone.list_microphone_names())
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
        # r.energy_threshold()
            print("Please answer in 1 word or a phrase : ")
            audio = r.listen(source, timeout=2, phrase_time_limit=6)
            try:
                text = r.recognize_google(audio)
                print("You answered '"+text+"'")
            except:
                text = "sorry, could not recognise"
                print("sorry, could not recognise")

        return text.lower()


class UserLoginForm(AuthenticationForm):
    answer1 = forms.CharField(label='Answer1')
    answer2 = forms.CharField(label='Answer2')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        un = kwargs.pop('username', None)
        # print(self.kwargs.get('username'))
        bot = ResponseBot()
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
            raise forms.ValidationError("Invalid Credentials")
        password = self.cleaned_data.get("password")
        if not user.check_password(password):
                # log auth tries
            raise forms.ValidationError("Invalid Credentials")
        # q1 = self.cleaned_data.get("question1")
        a1 = self.cleaned_data.get("answer1")
        # q2 = self.cleaned_data.get("question2")
        a2 = self.cleaned_data.get("answer2")
        # if user.question1 != q1 or user.question2 != q2:
        # raise forms.ValidationError("Incorrect Question")
        print(a1)
        print(a2)
        if a1 == None or a2 == None:
            raise forms.ValidationError("Incorrect response")
        flag1 = 0
        flag2 = 0
        for user.answer1 in a1:
            flag1 = 1
            break
            print("1yes")
        for user.answer2 in a2:
            flag2 = 1
            break
        if flag1 != 1 or flag2 != 1:
            raise forms.ValidationError("Incorrect response")
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UsernameForm(forms.Form):
    username = forms.CharField(label='Username')

    def clean_username(self):
        un = self.cleaned_data.get('username')
        print(un)
        qs = Account.objects.filter(username=un)
        print(qs)
        if qs.count() == 0:
            raise forms.ValidationError('Username does not exists')
        return un


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
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

    def __init__(self, username=None, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Account.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_question2(self):
        q1 = self.cleaned_data.get("question1")
        q2 = self.cleaned_data.get("question2")
        print(q1)
        print(q2)
        if q1.question == q2.question:
            raise forms.ValidationError("Please select 2 different questions")
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
