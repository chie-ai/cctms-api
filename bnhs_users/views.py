from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView, ListAPIView

from rest_framework import status

from covid19_case_records.serializers import *
from covid19_case_records.models import *
from .serializers import *
from .models import BNHSUser, UserNumber, Grade, HealthCareService

from .pagination import UserPagination
from datetime import datetime
from django.db.models import Max

# from django.core.files.storage import FileSystemStorage
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import filters
# from django.db.models import OuterRef, Subquery

class DashBoard(ListAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        try:
            exlcude_classification = ['uninfected covid-19 case', 'recovered covid-19 case']
            covid19_case = CovidCaseRecord.objects.filter(
                created_at__in=CovidCaseRecord.objects.values('user_id') \
                .annotate(
                    timestamp__max=Max('created_at')
                ).values('timestamp__max')
            ) \
            .exclude(classification__in=exlcude_classification) \
            .values('user_id').count()
            recovered_covid19_case = CovidCaseRecord.objects.filter(
                classification='recovered covid-19 case',
                created_at__in=CovidCaseRecord.objects.values('user_id') \
                .annotate(
                    timestamp__max=Max('created_at')
                ).values('timestamp__max')
            ) \
            .values('user_id').count()
            student = BNHSUser.objects.filter(usertype='student').count()
            teacher = BNHSUser.objects.filter(usertype='teacher').count()
            staff = BNHSUser.objects.filter(usertype='staff').count()
            health_care_staff = BNHSUser.objects.filter(usertype='health care staff').count()
            admin = BNHSUser.objects.filter(usertype='admin').count()
            content = {
                'covid19_case': str(covid19_case),
                'recovered_covid19_case': str(recovered_covid19_case),
                'student': str(student),
                'teacher': str(teacher),
                'staff': str(staff),
                'health_care_staff': str(health_care_staff),
                'admin': str(admin)
            }
            return Response(content, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RegisterUserInfoView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope] # use this if authentication and token are needed

    def post(self, request):
        serializer = BNHSUsersSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            self.save_user_number(request, user)
            usertype = request.data['usertype']

            if (usertype == 'student'):
                self.save_grade(request, user)

            if (usertype != 'health care staff'):
                self.save_covid_status(request, user)

            if (usertype == 'health care staff'):
                self.save_health_care_service(request, user)

            return Response(user.pk, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def save_user_number(self, request, user):
        user_number=request.data['user_number']
        serializer = UserNumberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user.pk)

    def save_grade(self, request, user):
        serializer = GradeSerializer(data=request.data)
        # gradeSerializer = GradeSerializer(data=request.data, context={'foreignKey': user.pk})
        if serializer.is_valid():
            # gradeSerializer.save()
            serializer.save(student_id=user.pk)

    def save_covid_status(self, request, user):
        serializer = CovidCaseRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user.pk)

    def save_health_care_service(self, request, user):
        serializer = HealthCareServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user.pk)

class UpdateUserInfo(ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def put(self, request, pk, format=None):
        user_info = BNHSUser.objects.get(pk=pk)
        serializer = UserSerializer(user_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.save_user_number(request)

            usertype=request.data['usertype']
            if (usertype == 'student'):
                self.save_grade(request)

            if (usertype == 'health care staff'):
                self.save_health_care_service(request)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(saved_user.errors, status=status.HTTP_400_BAD_REQUEST)

    def save_user_number(self, request):
        user_id = request.data['user_id']
        user_number_object = UserNumber.objects.get(user_id=user_id)
        serializer = UserNumberSerializer(user_number_object, data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user_id, user_number=request.data['user_number'])

    def save_grade(self, request):
        user_id = request.data['user_id']
        user_object = Grade.objects.get(student_id=user_id)
        serializer = GradeSerializer(user_object, data=request.data)
        if serializer.is_valid():
            serializer.save(student_id=user_id, level=request.data['level'])

    def save_health_care_service(self, request):
        user_id = request.data['user_id']
        health_center = HealthCareService.objects.get(user_id=user_id)
        serializer = HealthCareServiceSerializer(health_center, data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=user_id, health_care_service=request.data['health_care_service'])

# Retreive student number if exist
class CheckUserNumber(RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        try:
            user_number = request.query_params['user_number']
            queryset = UserNumber.objects.get(user_number=user_number)
            serializer = UserNumberSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserNumber.DoesNotExist:
            queryset = UserNumber.objects.none()
            serializer = UserNumberSerializer(queryset)
            return Response(serializer.data)

class GetUserList(ListAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    
    serializer_class = BNHSUsersSerializer
    pagination_class = UserPagination
    # filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        usertype = self.request.query_params.get('usertype', False)
        usernumber = self.request.query_params.get('user_number__user_number', '')
        firstname = self.request.query_params.get('first_name', '')
        middlename = self.request.query_params.get('middle_name', '')
        lastname = self.request.query_params.get('last_name', '')
        classification = self.request.query_params.get('covid19_status__classification', '')
        if usertype == 'admin':
            exclude_usertype = []
        else:
            exclude_usertype = ['others']
        if (usertype == 'covid-19 case' or usertype == 'recovered covid-19 case'):
            user_ids = self.get_covid19_case(usertype, classification)
            # filterset_fields = ['usertype', 'user_number__user_number', 'first_name', 'middle_name', 'last_name', 'covid19_status__classification']
            if (usernumber != '' or firstname != '' or middlename != '' or lastname != ''):
                users = BNHSUser.objects \
                    .filter(
                        pk__in=user_ids,
                        user_number__user_number__contains=usernumber,
                        first_name__icontains=firstname,
                        middle_name__icontains=middlename,
                        last_name__icontains=lastname,
                        covid19_status__classification__icontains=classification
                    ) \
                    .exclude(usertype__in=exclude_usertype).annotate(
                        timestamp__max=Max('covid19_status__created_at')
                    ).order_by('-timestamp__max')
                if (users.exists()):
                    return users
                else:
                    return BNHSUser.objects.none()
            else:
                return BNHSUser.objects.filter(pk__in=user_ids) \
                    .exclude(usertype__in=exclude_usertype).annotate(
                        timestamp__max=Max('covid19_status__created_at')
                    ).order_by('-timestamp__max')
        else:
            # filterset_fields = ['usertype', 'user_number__user_number', 'first_name', 'middle_name', 'last_name']
            if (usernumber != '' or firstname != '' or middlename != '' or lastname != ''):
                users = BNHSUser.objects \
                    .filter(
                        usertype=usertype,
                        user_number__user_number__contains=usernumber,
                        first_name__icontains=firstname,
                        middle_name__icontains=middlename,
                        last_name__icontains=lastname
                    ) \
                    .exclude(usertype__in=exclude_usertype) \
                    .order_by('last_name')
                if (users.exists()):
                    return users
                else:
                    return BNHSUser.objects.none()
            else:
                return BNHSUser.objects.filter(usertype=usertype).exclude(usertype__in=exclude_usertype).order_by('last_name')

    def get_covid19_case(self, usertype, _classification):
        classification = []
        if (usertype == 'covid-19 case'):
            classification = ['recovered covid-19 case', 'uninfected covid-19 case']
            if (_classification == 'suspect covid-19 case'):
                classification.extend(['probable covid-19 case', 'confirmed covid-19 case'])
            elif (_classification == 'probable covid-19 case'):
                classification.extend(['suspect covid-19 case', 'confirmed covid-19 case'])
            elif (_classification == 'confirmed covid-19 case'):
                classification.extend(['suspect covid-19 case', 'probable covid-19 case'])
        else:
            classification = ['uninfected covid-19 case', 'suspect covid-19 case', 'probable covid-19 case', 'confirmed covid-19 case']

        user_id = CovidCaseRecord.objects.filter(
            created_at__in=CovidCaseRecord.objects.values('user_id') \
            .annotate(
                timestamp__max=Max('created_at')
            ).values('timestamp__max')
        ) \
        .exclude(classification__in=classification) \
        .values('user_id')
        # print(user_id)
        return user_id

class CheckUsername(RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        try:
            username = request.query_params['username']
            queryset = BNHSUser.objects.get(username=username)
            serializer = UserNameSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BNHSUser.DoesNotExist:
            queryset = BNHSUser.objects.none()
            serializer = UserNameSerializer(queryset)
            return Response(serializer.data)

class GetUserInfo(RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def get_object(self, pk):
        try:
            return BNHSUser.objects.get(pk=pk)
        except BNHSUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = BNHSUsersSerializer(user)
        return Response(serializer.data)

class GetUserCovid19History(ListAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    serializer_class = CovidCaseRecordSerializer

    def get_queryset(self):
        user_id = self.request.query_params['user_id']
        return CovidCaseRecord.objects.filter(user_id=user_id).order_by('-created_at')

    # Turning off pagination on this class
    def paginate_queryset(self, queryset):
        if self.paginator and self.request.query_params.get(self.paginator.page_query_param, None) is None:
            return None
        return super().paginate_queryset(queryset)
    
class AddCovid19Status(ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def post(self, request):
        serializer = CovidCaseRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.data['user_id'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecordVaccination(ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def post(self, request):
        serializer = VaccinationRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.data['user_id'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetVaccineRecords(ListAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    serializer_class = VaccinationRecordSerializer

    def get_queryset(self):
        user_id = self.request.query_params['user_id']
        return VaccinationRecord.objects.filter(user_id=user_id).order_by('-vaccinated_at')

    # Turning off pagination on this class
    def paginate_queryset(self, queryset):
        if self.paginator and self.request.query_params.get(self.paginator.page_query_param, None) is None:
            return None
        return super().paginate_queryset(queryset)

class AddUserProfile (ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def post(self, request):
        # user_profile = request.FILES['profile']
        # fs = FileSystemStorage()
        # filename = fs.save(user_profile.name, user_profile)
        # image_url = fs.url(filename)
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.data['user_id'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateUserProfile(ListCreateAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def put(self, request, pk, format=None):
        profile = UserProfile.objects.get(user_id=pk)
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChangePassword(ListAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def post(self, request):
        serializer = PasswordChangeSerializer(context={'request': request}, data=request.data)
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetCurrentUserInformation(RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        try:
            queryset = BNHSUser.objects.get(username=self.request.user)
            serializer = UserSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BNHSUser.DoesNotExist:
            queryset = BNHSUser.objects.none()
            serializer = UserSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

class VerifyUserHealthCondition(RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def get(self, request):
        try:
            user_id = self.get_user(request)
            queryset = BNHSUser.objects.filter(id__in=user_id).exclude(usertype='health care staff').distinct('id')
            serializer = BNHSUsersSerializer(queryset, many=True) 
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BNHSUser.DoesNotExist:
            queryset = BNHSUser.objects.none()
            serializer = BNHSUsersSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def get_user(self, request):
        user = UserNumber.objects.filter(user_number=request.query_params['user_number']).distinct('user_id').values('user_id')
        return user

class DeleteUserRecord(GenericAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def get_object(self, pk):
        try:
            return BNHSUser.objects.get(pk=pk)
        except BNHSUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    