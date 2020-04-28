from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, get_user_model, logout
from django.views.generic import View, DetailView, CreateView, UpdateView, TemplateView, FormView
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse_lazy, reverse
from .forms import RegisterForm
from django.db.models import Q
from .models import Account, Question, Generalq
from .forms import RegisterForm, UsernameForm, UserLoginForm
from Voice_Auth import settings
from gtts import gTTS
import os
import random
import time
import io
from google.cloud import texttospeech
from google.cloud import translate
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums
from django.utils import translation

from django.core.files.storage import FileSystemStorage, Storage
from .storage import OverwriteStorage
from django.http import HttpResponse


translate_client = translate.Client()
client = texttospeech.TextToSpeechClient()
# Flag = 1 for Hindi


class ResponseBot:

    def __init__(self):
        print('Bot Created')

    def askQuestion(self, l, r):
        index = random.randint(l, r)
        return index

    def verifyResponse(self, answers, response, index):
        for i in answers[index]:
            if i in response:
                return True
        return False

    def getResponse(self, username, no_, flag):
        client = speech_v1p1beta1.SpeechClient()
        lang_code = 'en-IN'
        if flag == 1:
            lang_code = 'hi'
        sample_rate_hertz = 16000
        # Encoding of audio data sent. This sample sets this explicitly.
        # This field is optional for FLAC and WAV audio formats.
        encoding = enums.RecognitionConfig.AudioEncoding.MP3
        config = {
            "language_code": lang_code,
            # "sample_rate_hertz": sample_rate_hertz,
            # verify audio_channel_count
            "audio_channel_count": 1,
            # "encoding": encoding,
        }
        uri = settings.MEDIA_ROOT + "/" + username + "-/a" + no_ + ".wav"
        with io.open(uri, "rb") as f:
            content = f.read()
        audio = {"content": content}
        response = client.recognize(config, audio)
        text = "dummy"
        if response.results:
            text = response.results[0].alternatives[0].transcript
        for result in response.results:
            # First alternative is the most probable result
            alternative = result.alternatives[0]
            print(u"Transcript: {}".format(alternative.transcript))
        return text.lower()

    def deliverResponse(self, text, index, flag, host):
        print(settings.MEDIA_ROOT)
        # os.startfile(settings.MEDIA_ROOT+'1.mp3')
        print(text)
        # For Hindi
        lang_code = 'en-IN'
        if flag == 1:
            lang_code = 'hi'
        synthesis_input = texttospeech.types.SynthesisInput(text=text)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=lang_code, ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        response = client.synthesize_speech(synthesis_input, voice, audio_config)

        with open(settings.MEDIA_ROOT + '/output'+str(index)+'.mp3', 'wb') as out:
            out.write(response.audio_content)
        return 'http://' + host + settings.MEDIA_URL + 'output'+str(index)+'.mp3'


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('index')


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
    return redirect(reverse_lazy('index'))


class LoginView(FormView):
    success_url = reverse_lazy('index')
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
        i1 = bot.askQuestion(1, 10)
        i2 = bot.askQuestion(11, 20)
        q3 = Generalq.objects.get(pk=i1)
        q4 = Generalq.objects.get(pk=i2)
        print(q1.pk)
        print(q2.pk)
        # response = bot.getResponse()
        # print(response)
        host = self.request.get_host()
        link1 = bot.deliverResponse(q1.question, 1, flag, host)
        link2 = bot.deliverResponse(q2.question, 2, flag, host)
        link3 = bot.deliverResponse(q3.question, 3, flag, host)
        link4 = bot.deliverResponse(q4.question, 4, flag, host)
        context['link1'] = link1
        context['link2'] = link2
        context['link3'] = link3
        context['link4'] = link4
        context['gq1'] = i1
        context['gq2'] = i2
        return context


class LogoutPage(TemplateView):
    template_name = 'accounts/logout-page.html'


class IndexView(TemplateView):
    template_name = 'accounts/index.html'


def AudioStt(request):
    bot = ResponseBot()
    audio = request.FILES['audio']
    username = request.POST.get('username', None)
    no_ = request.POST.get('no_', None)
    print(username)
    print(no_)
    success = True
    if audio == None:
        success = False
        print("Audio not received")
    else:
        location = settings.MEDIA_ROOT + '/' + username + '-'
        fs = OverwriteStorage(location=location)
        fs.save(audio.name, audio)
    if translation.get_language() == "en":
        flag = 0
    else:
        flag = 1
    text = bot.getResponse(username, no_, flag)
    if text == "dummy":
        success = False
    data = {
        'text': text,
        'success': success
    }
    return JsonResponse(data)
