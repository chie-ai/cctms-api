from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import os

class MyUserManager(BaseUserManager):
    def create_user(self, username, is_admin, password=None):
        """
        Creates and saves a User with the given fields.
        """
        user = self.model(
            username=username,
            is_admin=is_admin
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, is_admin, password=None):
        """
        Creates and saves a superuser with the given fields.
        """
        user = self.create_user(
            username,
            is_admin,
            password=password,
        )
        user.save(using=self._db)
        return user

class BNHSUser(AbstractBaseUser):
    ADMIN = 'admin'
    STUDENT = 'student'
    TEACER = 'teacher'
    STAFF = 'staff'
    HEALTH_CARE_STAFF = 'health care staff'
    DJANGO_ADMIN = 'django-admin'

    USER_TYPE = (
        (ADMIN, ADMIN),
        (STUDENT, STUDENT),
        (TEACER, TEACER),
        (STAFF, STAFF),
        (HEALTH_CARE_STAFF, HEALTH_CARE_STAFF),
        (DJANGO_ADMIN, DJANGO_ADMIN)
    )

    MALE = 'male'
    FEMALE = 'female'

    SEX = (
        (MALE, MALE),
        (FEMALE, FEMALE)
    )
    username = models.CharField(max_length=100, null=True, unique=True)
    first_name = models.CharField(max_length=100, blank=True, default='')
    middle_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    sex = models.CharField(max_length=100, choices=SEX, default=MALE)
    address = models.CharField(max_length=100, blank=True, default='')
    contact_number = models.CharField(max_length=100, blank=True, default='')
    usertype = models.CharField(max_length=255, choices=USER_TYPE, default=DJANGO_ADMIN)
    email = models.EmailField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['is_admin']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class UserNumber(TimeStampedModel):
    # user_id = models.PositiveBigIntegerField(blank=True, unique=True)
    user = models.OneToOneField(BNHSUser, on_delete=models.CASCADE, blank=True, null=True, related_name="user_number")
    user_number = models.PositiveBigIntegerField(default=0, blank=True, null=True, unique=True)

    def __str__(self):
        return str(self.user_number)

from random import randrange
def update_filename(self, filename):
    path = 'profile/'
    main_path = '/home/project/backend/cctms-backend/mediafiles/profile/'
    ext = filename.split('.')[-1]
    filename = "%s%s.%s" % (self.user, randrange(500), ext)

    for suffix in range(501):
        remove_filename = "%s%s.%s" % (self.user, suffix, ext)
        if os.path.isfile(os.path.join(main_path, remove_filename)):
            os.remove(os.path.join(main_path, remove_filename))
            break

    return os.path.join(path, filename)

class UserProfile (TimeStampedModel):
    user = models.OneToOneField(BNHSUser, on_delete=models.CASCADE, blank=True, null=True, related_name="user_profile")
    profile_file = models.ImageField(upload_to=update_filename, blank=True, null=True)

    def __str__(self):
        return str(self.profile_file)

class Grade(TimeStampedModel):
  SEVEN = 'seven'
  EIGHT = 'eight'
  NINE = 'nine'
  TEN = 'ten'
  ELEVEN = 'eleven'
  TWELVE = 'twelve'

  GRADE_LEVELS = (
    (SEVEN, SEVEN),
    (EIGHT, EIGHT),
    (NINE, NINE),
    (TEN, TEN),
    (ELEVEN, ELEVEN),
    (TWELVE, TWELVE)
  )
  student = models.OneToOneField(BNHSUser, on_delete=models.CASCADE, related_name="grade_level")
  level = models.CharField(max_length=255, choices=GRADE_LEVELS, default=SEVEN)

  def __str__(self):
    return str(self.level)

class HealthCareService(TimeStampedModel):
  user = models.OneToOneField(BNHSUser, on_delete=models.CASCADE, related_name="health_care_service")
  health_care_service = models.CharField(max_length=255, blank=True, default='')

  def __str__(self):
    return self.health_care_service
