from modeltranslation.translator import translator, TranslationOptions
from accounts.models import Question, Account, Generalq


class QuestionTranslationOptions(TranslationOptions):
    fields = ('question',)


class AccountTranslationOptions(TranslationOptions):
    fields = ('answer1', 'answer2',)


class GeneralqTranslationOptions(TranslationOptions):
    fields = ('question', 'answer',)


translator.register(Question, QuestionTranslationOptions)
translator.register(Account, AccountTranslationOptions)
translator.register(Generalq, GeneralqTranslationOptions)
