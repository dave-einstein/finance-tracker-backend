from django.db import models
from uuid import uuid4
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser,UserManager,Group,Permission
import random
import string

def generateID():
    ID = ""
    for i in range(2):
        ID += str(random.choice(string.ascii_uppercase))

    for _ in range(10):
        ID += str(random.randint(0,9))
    return ID

class User(AbstractUser):
    # Specify unique related_name values to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name="backend_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="backend_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    user_id = models.CharField(max_length=50,primary_key=True)
    first_name = models.CharField(max_length=50,blank=False,verbose_name='Firt Name')
    last_name = models.CharField(max_length=50,blank=False,verbose_name='Last Name')
    username = models.CharField(max_length=50,unique=True,verbose_name='Username')
    email = models.EmailField(unique = True,verbose_name='Email')
    currency = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add = True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return (f"{self.username}")
    
    def save(self,*args,**kwargs):
        self.user_id = generateID()
        self.first_name = self.first_name.upper()
        self.last_name = self.last_name.upper()
        return super().save(*args,**kwargs)

class Budget(models.Model):
    id = models.CharField(primary_key=True,unique=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    year = models.IntegerField()
    month = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_created=True,default=now)

    def save(self,*args, **kwargs):
        self.id = generateID()
        return super().save(*args, **kwargs)
    
class Income(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4,editable=False)
    description = models.CharField(max_length=50)
    budget = models.ForeignKey(Budget,on_delete=models.CASCADE)
    income_type = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_created=True,default=now)

class Savings(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4,editable=False)
    description = models.CharField(max_length=50)
    budget = models.ForeignKey(Budget,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_created=True,default=now)

class Investment(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4,editable=False)
    description = models.CharField(max_length=50)
    budget = models.ForeignKey(Budget,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_created=True,default=now)

class Expense(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4,editable=False)
    budget = models.ForeignKey(Budget,on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_created=True,default=now)
