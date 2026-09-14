from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from features.staffs.models import Staff
from django.utils import timezone
from .user_manager import UserManager
from allauth.account.models import EmailAddress
# Create your models here.
class MogUser(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, unique=False)

    staff = models.OneToOneField(
        Staff,
        on_delete=models.CASCADE,
        related_name="user",
        null=True,
        blank=True
    )

    is_active=models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            last_user = MogUser.objects.order_by("-id").first()
            if last_user and last_user.user_id:
                last_number = int(last_user.user_id.split("-")[1])
                next_id = last_number + 1
            else:
                next_id = 1
            self.user_id = f"USR-{next_id:03d}"

        print("it is about to save!")
        super().save(*args, **kwargs)

