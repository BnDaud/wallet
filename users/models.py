from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from uuid import uuid4


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    email = models.EmailField(unique=True)
    username = None
    
    first_name = models.CharField(max_length=150 ,)
    last_name = models.CharField(max_length=150)
    
    # 2. KYC Tracking
    is_kyc_verified = models.BooleanField(default=False)
    kyc_verified_key = models.CharField(max_length=255, blank=True, null=True)



    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    is_created = models.DateTimeField(auto_now_add =True ,null= True)
    is_updated = models.DateTimeField(auto_now=True , null=True)

    objects = UserManager()