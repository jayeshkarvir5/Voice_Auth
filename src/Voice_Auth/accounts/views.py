from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, get_user_model, logout
from django.views.generic import View, DetailView, CreateView, UpdateView, TemplateView, FormView
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse_lazy, reverse
from .forms import RegisterForm
from django.db.models import Q
from .models import Account, Question
from .forms import RegisterForm, UsernameForm, UserLoginForm
from Voice_Auth import settings
import speech_recognition as sr
from gtts import gTTS
import os
import random
import time
from google.cloud import texttospeech
from google.cloud import translate
from django.utils import translation


translate_client = translate.Client()
client = texttospeech.TextToSpeechClient()
# Flag = 1 for Hindi
flag = 1


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

    def deliverResponse(self, text, index, flag):
        # language = 'en'
        # myobj = gTTS(text=text, lang=language, slow=False)
        # myobj.save(settings.MEDIA_ROOT+'/output'+str(index)+'.mp3')
        print(settings.MEDIA_ROOT)
        # os.startfile(settings.MEDIA_ROOT+'1.mp3')

        # For Hindi
        if flag == 1:
            translation = translate_client.translate(text, target_language='hi')
            text = translation['translatedText']
            print(translation['translatedText'])

            synthesis_input = texttospeech.types.SynthesisInput(text=text)
            voice = texttospeech.types.VoiceSelectionParams(
                language_code='hi', ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
            audio_config = texttospeech.types.AudioConfig(
                audio_encoding=texttospeech.enums.AudioEncoding.MP3)
            response = client.synthesize_speech(synthesis_input, voice, audio_config)
        else:
            synthesis_input = texttospeech.types.SynthesisInput(text=text)
            voice = texttospeech.types.VoiceSelectionParams(
                language_code='en-IN', ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
            audio_config = texttospeech.types.AudioConfig(
                audio_encoding=texttospeech.enums.AudioEncoding.MP3)
            response = client.synthesize_speech(synthesis_input, voice, audio_config)

        with open(settings.MEDIA_ROOT + '/output'+str(index)+'.mp3', 'wb') as out:
            out.write(response.audio_content)
        return 'http://127.0.0.1:8000' + settings.MEDIA_URL + 'output'+str(index)+'.mp3'


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('accounts:index')


class UnView(FormView):
    form_class = UsernameForm
    template_name = 'accounts/enter-un.html'

    def form_valid(self, form):
        print('here'+form.cleaned_data.get('username'))
        username = form.cleaned_data.get('username')
        self.success_url = reverse_lazy('accounts:login', kwargs={'username': username})
        return super(UnView, self).form_valid(form)


def LogoutView(request):
    logout(request)
    return redirect('/accounts/index/')


class LoginView(FormView):
    success_url = reverse_lazy('accounts:index')
    template_name = "registration/login.html"
    form_class = UserLoginForm

    def form_valid(self, form):
        # print(self.kwargs.get('username'))
        # print(form.answer1)
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        if translation.get_language() == "en":
            flag = 0
        else:
            flag = 1
        context = super(LoginView, self).get_context_data(*args, **kwargs)
        username = self.kwargs.get('username')
        user = Account.objects.get(username=username)
        context['user'] = user
        bot = ResponseBot()
        q1 = Question.objects.get(question=user.question1)
        q2 = Question.objects.get(question=user.question2)
        print(q1.pk)
        print(q2.pk)
        # response = bot.getResponse()
        # print(response)
        link1 = bot.deliverResponse(q1.question, 1, flag)
        link2 = bot.deliverResponse(q2.question, 2, flag)
        context['link1'] = link1
        context['link2'] = link2
        return context


class LogoutPage(TemplateView):
    template_name = 'accounts/logout-page.html'


class IndexView(TemplateView):
    template_name = 'accounts/index.html'
