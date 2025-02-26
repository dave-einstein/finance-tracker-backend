from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser,UserManager,Group,Permission
import random
import string

def generateUserID():
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
        self.user_id = generateUserID()
        self.first_name = self.first_name.upper()
        self.last_name = self.last_name.upper()
        return super().save(*args,**kwargs)
    

class Transactions(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'income'),
        ('expenses', 'expenses'),
        ('savings', 'savings'),
        ('investment', 'investment'),
        )
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_payment', 'Mobile Payment'),
    ]
    RECURRING_FREQUENCY = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    transaction_id = models.UUIDField(primary_key=True,default=uuid4,editable=False)
    transaction_type = models.CharField(max_length=10,choices=TRANSACTION_TYPES,default='expenses')
    category = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=100,null=True,blank=True)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='cash')
    is_recurring = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=RECURRING_FREQUENCY, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"