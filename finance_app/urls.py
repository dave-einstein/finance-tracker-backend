from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import *

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/signup',SignupView.as_view(),name="signup"),
    path('api/login',LoginView.as_view(),name="login"),
    path('api/confirm-email',ConfirmEmail.as_view(),name="confirm-email"),
    # path('api/forget-password',ForgetPassword.as_view(),name="forget-password"),
    # path('api/reset-password',ResetPassword.as_view(),name="reset-password"),
    path('api/logout',SignoutView.as_view(),name="logout"),
    path('api/budget',BudgetView.as_view(),name="budget")

]
