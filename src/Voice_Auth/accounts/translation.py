from modeltranslation.translator import translator, TranslationOptions
from accounts.models import Question


class QuestionTranslationOptions(TranslationOptions):
    fields = ('question',)


translator.register(Question, QuestionTranslationOptions)
