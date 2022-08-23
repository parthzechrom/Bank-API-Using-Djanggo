
from re import T
from statistics import mode
from django.db import models
from .models import *
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import UserManager

# Create your models here.



class CustomUser(AbstractBaseUser):
    id=models.AutoField(primary_key=True,db_column="id")
    username = models.CharField(max_length=255,db_column="username",unique=True,null=False)
    email = models.EmailField(max_length=255,db_column="email",unique=True,null=False)
    password = models.CharField(max_length=255,db_column="password",null=False)
    is_staff= models.BooleanField(default=False)
    address=models.CharField(max_length=255,db_column="address",null=True)
    contact=models.BigIntegerField(db_column="contact",null=True)
    bankadmin=models.CharField(max_length=255,db_column="bankadmin",null=True)
    account_number=models.BigIntegerField(db_column="account_NO",unique=True,null=True)
    ifsc=models.CharField(max_length=255,default='ABC00012',null=True)
    pin_number=models.IntegerField(db_column="pin_no",null=True)
    account_type=models.CharField(max_length=255,db_column="account_type",null=True)
    block=models.BooleanField(db_column="block_user",default=False)
    
    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        db_table = "user_table"


class UserAccountModel(models.Model):
    userId=models.ForeignKey(CustomUser,db_column="userId",on_delete=models.CASCADE)
    debit = models.DecimalField(db_column="debit",max_digits=12, decimal_places=2,null=True,default=0)
    credit = models.DecimalField(db_column="credit",max_digits=12, decimal_places=2,null=True,default=0)
    balance = models.DecimalField(db_column="balance",max_digits=12, decimal_places=2,null=True,default=0)
    amount = models.DecimalField(db_column="amount",max_digits=12, decimal_places=2,null=True,default=0)
    trans_id = models.BigIntegerField(db_column="trans_account_no",null=True,default=0)

    def __str__(self):
         return '{} {} {} {} {} {}'.format(self.userId,self.debit, self.credit
        ,self.balance,self.amount,self.trans_id)

    def __as_dict__(self):
        return {
            "debit": self.debit,
            "amount": self.credit,
            "balance": self.balance,
            "amount": self.amount,
            "userId": self.userId,
            "trans_id":self.trans_id,

        }

    class Meta:
        db_table = "user_account_table"

    
class BalanceViewModel(models.Model):
    id=models.AutoField(primary_key=True,db_column="id")
    userId=models.ForeignKey(CustomUser,db_column="userId",on_delete=models.CASCADE)
    balance=models.DecimalField(db_column="amount",max_digits=12, decimal_places=2,null=True,default=0)
    

    def __str__(self):
        return '{} {} {} '.format(self.id,self.userId,self.balance)

    def __as_dict__(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "balance":self.balance}
    class Meta:
        db_table = "user_balance_table"