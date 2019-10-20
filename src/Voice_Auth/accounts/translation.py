from modeltranslation.translator import translator, TranslationOptions
from accounts.models import Question, Account


class QuestionTranslationOptions(TranslationOptions):
    fields = ('question',)


class AccountTranslationOptions(TranslationOptions):
    fields = ('answer1', 'answer2',)


translator.register(Question, QuestionTranslationOptions)
translator.register(Account, AccountTranslationOptions)
