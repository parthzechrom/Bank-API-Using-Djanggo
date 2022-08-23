from tkinter import NO
from .models import *
from rest_framework import serializers
from .serilizer import *
import re
from rest_framework.validators import UniqueValidator
import random
from . import views
from .models import CustomUser

class AdminRegistration(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=CustomUser.objects.all(),
                                                               message="A user with that email address already exists.")])
    username = serializers.CharField(validators=[UniqueValidator(queryset=CustomUser.objects.all(),
                                                                 message="A user with that username already exists.")])

    def password_validator(values):
        pattern = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        test_string = values
        result = re.match(pattern, test_string)
        if not result:
            raise serializers.ValidationError(
                "Please enter Minimum eight characters,at least one letter,one number and one special character")

    password = serializers.CharField(
        write_only=True, validators=[password_validator])
    
    is_staff = serializers.BooleanField(default=True)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        # profile_data = validated_data.pop('bankadmin')
        # CustomUser.objects.create(user=user, **profile_data)
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user.set_password(password)
        user.is_active = True
        ifsc= None
        account_number= None
        pin_number= None
        user.account_number=account_number
        user.ifsc=ifsc
        user.pin_number=pin_number
        user.save()
        return user



class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=CustomUser.objects.all(),
                                                               message="A user with that email address already exists.")])
    username = serializers.CharField(validators=[UniqueValidator(queryset=CustomUser.objects.all(),
                                                                 message="A user with that username already exists.")])

    def password_validator(values):
        pattern = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        test_string = values
        result = re.match(pattern, test_string)
        if not result:
            raise serializers.ValidationError(
                "Please enter Minimum eight characters,at least one letter,one number and one special character")

    password = serializers.CharField(
        write_only=True, validators=[password_validator])
    account_type=serializers.CharField(allow_blank=False)
    is_staff = serializers.BooleanField(default=False)
    address=serializers.CharField(allow_null=False)
    contact=serializers.IntegerField(validators=[UniqueValidator(queryset=CustomUser.objects.all(),
                                                                 message="A user with that contact already exists.")])
    block= serializers.BooleanField(default=False)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        # profile_data = validated_data.pop('bankadmin')
        # CustomUser.objects.create(user=user, **profile_data)
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        account_type=validated_data['account_type']
        address=validated_data['address']
        contact=validated_data['contact']
        block_user=validated_data['block']
        user.set_password(password)
        ifsc= 'KKBK0005652'
        account_number= random.randint(1,10**12)
        pin_number= random.randint(1,10**4)
        user.account_number=account_number
        user.ifsc=ifsc
        user.pin_number=pin_number
        user.save()

        user_vo=BalanceViewModel()
        userID=CustomUser.objects.get(username=username)
        account_type=userID.account_type
        if account_type=='saving':
            amount=10000
            user_vo.userId=userID
            user_vo.balance=amount
            user_vo.save()
        else:
            amount=11000
            user_vo.userId=userID
            user_vo.balance=amount
            user_vo.save()

        return user


class UserAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = BalanceViewModel
        fields ="__all__"
    

class UserTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAccountModel
        fields ="__all__"