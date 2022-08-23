from django.urls import path,include
from . import views
from rest_framework_simplejwt.tokens import RefreshToken,Token

urlpatterns = [
    path('',views.UserRegistrationS.as_view({'get':'list','post':'create'}),name="Registration"),
    path('login/',views.LoginAPI.as_view({'get':'list','post':'create'})),
    # path('registration/',views.UserRegistrationS.as_view({'get':'list','post':'create'})),
    path('balance/',views.BalanceAPI.as_view({'get':'list','post':'create'})),
    path('balanceview/',views.BalanceviewsAPI.as_view()),
    path('transaction/',views.TransactionAPI.as_view()),
    path('block/',views.BlockUserAPI.as_view()),
    path('logout/',views.Logout.as_view()),
    path('withdraw/',views.WithdrawAPI.as_view())

]

