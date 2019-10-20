from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

USERNAME_REGEX = '^[a-zA-Z0-9.+-]*$'


class Question(models.Model):
    question = models.TextField()

    def __str__(self):
        return self.question


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=255,
                                validators=[
                                    RegexValidator(
                                        regex=USERNAME_REGEX,
                                        message=_(
                                            'Username must be Alpahnumeric or contain any of the following: ". @ + -" '),
                                        code='invalid_username'
                                    )],
                                unique=True,)
    question1 = models.ForeignKey(Question, related_name='first',
                                  on_delete=models.CASCADE, null=True)
    question2 = models.ForeignKey(Question, related_name='second',
                                  on_delete=models.CASCADE, null=True)
    answer1 = models.CharField(max_length=50, null=True)
    answer2 = models.CharField(max_length=50, null=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True
