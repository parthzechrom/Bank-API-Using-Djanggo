
from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from .serilizer import *
from rest_framework.response import Response
from rest_framework.authentication import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authtoken.models import Token
import json
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken



# from django.contrib.auth.views import logout
# Create your views here.


# class RegistrationAPI(viewsets.ModelViewSet):

#     def create(self, request):
#         data = request.data
#         serializer = UserRegistrationSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             json_response = {"status": status.HTTP_201_CREATED,
#                              "header": "application/json", "message": "successfully Register..."}
#             return Response(json_response)
#         json_response = {"status": status.HTTP_403_FORBIDDEN,
#                          "response": serializer.errors, "message": "Register not success..."}
#         return Response(json_response)


class LoginAPI(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        # try:
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        user_block = user.block
        if user_block is False:
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({'message': 'successfully login',
                                'refresh': str(refresh),
                                 'access': str(refresh.access_token)},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'renter username & password'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"You are blocked"})

        # except Exception as ex:
        #     return Response(exception=ex)


class UserRegistrationS(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        data = request.data
        username = request.data.get('username')
        password = request.data.get('password')
        is_staff = request.data.get('is_staff')
        user = authenticate(username=username, password=password)
        if user is None:
            if is_staff == "True":
                data = request.data
                serializer = AdminRegistration(data=data)
            else:
                data = request.data
                serializer = UserRegistrationSerializer(data=data)
            if serializer.is_valid():
                serializer.save(bankadmin=self.request.user.id)
                json_response = {"status": status.HTTP_201_CREATED,
                                 "header": "application/json", "message": "successfully Register..."}
                return Response(json_response)
            json_response = {"status": status.HTTP_403_FORBIDDEN,
                             "response": serializer.errors, "message": "Register not success..."}
            return Response(json_response)
        else:
            return Response({'message': 'already registrant'})


class BalanceAPI(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    user = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'transaction'

    def create(self, request, *args, **kwargs):
        account_no = request.data.get("account_number")
        ifsc = request.data.get("ifsc")
        amount = request.data.get("amount")
        pin = request.data.get("pin")
        credit_user = CustomUser.objects.get(
            account_number=account_no, ifsc=ifsc)
        user_block = credit_user.block
        if user_block is False:
            if credit_user is not None:
                userid = request.user.id
                user = BalanceViewModel.objects.get(userId=userid)
                user_account_no = user.userId.account_number
                user_pin = user.userId.pin_number

                if pin == user_pin:
                    debit_userId = CustomUser.objects.get(id=userid)
                    print(debit_userId)
                    account_type = debit_userId.account_type
                    credit_userId = credit_user.id
                    user_balance = user.balance
                    Amount = user_balance-amount
                    user.balance = Amount
                    user.save()
                    balance_check = (account_type == "saving" and 5000 <= Amount) or (
                        account_type == "current" and 10000 <= Amount)
                    if balance_check is True:
                        user_vo = UserAccountModel()
                        user_vo.amount = Amount
                        user_vo.debit = amount
                        user_vo.balance = user_balance
                        user_vo.userId = debit_userId
                        user_vo.trans_id = account_no
                        user_vo.save()
                        if user_vo is not None:
                            credit_user_vo = UserAccountModel()
                            User = BalanceViewModel.objects.get(
                                userId=credit_userId)
                            credit_balance = User.balance
                            credit_amount = credit_balance + amount
                            User.balance = credit_amount
                            User.save()
                            credit_user_vo.trans_id = user_account_no
                            credit_user_vo.amount = credit_amount
                            credit_user_vo.balance = credit_balance
                            credit_user_vo.credit = amount
                            credit_user_vo.userId = credit_user
                            credit_user_vo.save()
                            return Response({'message': "your account in credited amount",
                                             "credit": amount, "balance": credit_amount}, status=status.HTTP_200_OK)
                    else:
                        debit_userId = CustomUser.objects.get(id=userid)
                        print(debit_userId)
                        account_type = debit_userId.account_type
                        credit_userId = credit_user.id
                        user_balance = user.balance
                        Amount = user_balance+amount
                        user.balance = Amount
                        user.save()
                        return Response({"message": "your account in not valid balance available"}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({'message': "your account in credited amount"}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'message': 'renter pin'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'error': "user is not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": " this account user is blocked"}, status=status.HTTP_400_BAD_REQUEST)


class BalanceviewsAPI(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        userId = self.request.user.id
        queryset = (BalanceViewModel.objects.filter(userId__bankadmin=userId)) or (
            BalanceViewModel.objects.filter(userId=userId))
        if queryset is not None:
            serializer = UserAccountSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionAPI(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        userId = self.request.user.id
        user_vo = UserAccountModel.objects.filter(
            userId__bankadmin=userId) or UserAccountModel.objects.filter(userId=userId)
        if user_vo is not None:
            serializer = UserTransactionSerializer(user_vo, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class WithdrawAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'withdraw'

    def post(self, request):
        amount = request.data.get('amount')
        pin = request.data.get("pin")
        user = CustomUser.objects.get(pin_number=pin)
        if user is not None:
            user_vo = BalanceViewModel.objects.get(userId=user.id)
            balance = user_vo.balance
            userid = user_vo.userId
            Amount = balance-amount
            user_vo.balance = Amount
            user_vo.save()
            if user_vo is not None:
                credit_user_vo = UserAccountModel()
                credit_user_vo.credit = amount
                credit_user_vo.balance = balance
                credit_user_vo.amount = Amount
                credit_user_vo.userId = user
                credit_user_vo.save()
                return Response({'message': 'withdraw successfully complete', 'balance': Amount,
                                 'withdraw': amount}, status=status.HTTP_202_ACCEPTED)
            else:
                user_vo = BalanceViewModel.objects.get(userId=user.id)
                balance = user_vo.balance
                userid = user_vo.userId
                Amount = balance-amount
                user_vo.balance = Amount
                user_vo.save()
                return Response({"error": "your withdraw transaction is uncompleted"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return RefreshToken({"ERROR": 'please renter pin '}, status=status.HTTP_400_BAD_REQUEST)


class BlockUserAPI(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        account_number = request.data.get('account_number')
        block = request.data.get('block')
        block_user = CustomUser.objects.get(account_number=account_number)
        if block_user is not None:
            block_user.block = block
            block_user.save()
            return Response({'message': "user successfully block"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "account number is invalid"})


class Logout(APIView):
    # permission_classes = (IsAuthenticated)
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        refresh_token = self.request.data.get('refresh')
        if refresh_token is None:
            Token = OutstandingToken.objects.filter(user=request.user)
            for token in Token:
                t, _ = BlacklistedToken.objects.get_or_create(token=token)
            return Response({"status": "OK, goodbye, all refresh tokens blacklisted"})
        else:
            token = RefreshToken(token=refresh_token)
            token.blacklist()
            return Response({"status": "refreshtoken logout"})
