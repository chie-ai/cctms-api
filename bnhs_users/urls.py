from django.urls import path
from .views import *

app_name = 'bnhs_users'
urlpatterns = [
  path(r'get-dashboard/', DashBoard.as_view(), name='dashboard'),
  path(r'register-user-info', RegisterUserInfoView.as_view(), name='register-user-info'),
  path(r'upload-user-profile', AddUserProfile.as_view(), name='upload-user-profile'),
  path(r'update-user-profile/<int:pk>/', UpdateUserProfile.as_view(), name='update-user-profile'),
  path(r'does-user-number-exist/', CheckUserNumber.as_view(), name='check-user-number'),
  path(r'does-username-exist/', CheckUsername.as_view(), name='check-username'),
  path(r'get-users-list/', GetUserList.as_view(), name='user-list'),
  path(r'record-vaccination', RecordVaccination.as_view(), name='record-vaccination'),
  path(r'get-vaccination-history/', GetVaccineRecords.as_view(), name='get-vaccine-records'),
  path(r'get-user-info/<int:pk>/', GetUserInfo.as_view(), name='user-info'),
  path(r'update-user-info/<int:pk>/', UpdateUserInfo.as_view(), name='update-user-info'),
  path(r'get-covid19-history/', GetUserCovid19History.as_view(), name='get-user-covid19-history'),
  path(r'add-covid19-status', AddCovid19Status.as_view(), name='add-covid19-status'),
  path(r'get-current-user-information', GetCurrentUserInformation.as_view(), name='get-current-user-information'),
  path(r'verify-user-health-condition/', VerifyUserHealthCondition.as_view(), name='verify-health-condition'),
  path(r'change-password', ChangePassword.as_view(), name='change-password'),
  path(r'delete-user/<int:pk>/', DeleteUserRecord().as_view(), name='delete-user')
]
