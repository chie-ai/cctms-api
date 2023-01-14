from rest_framework import serializers, fields
from .models import CovidCaseRecord, VaccinationRecord

class CovidCaseRecordSerializer(serializers.ModelSerializer):
    # def get_queryset(self):
    #     user = self.context['request'].user
    #     queryset = CovidCaseRecord.objects.filter(user=user)
    #     return queryset

    class Meta:
        model = CovidCaseRecord
        fields = ['user_id', 'classification', 'severity', 'created_at']

class VaccinationRecordSerializer(serializers.ModelSerializer):

    vaccinated_at = fields.DateField(input_formats=['%Y-%m-%d'])
    # input formats with time: `%Y-%m-%dT%H:%M:%S.%fZ`

    class Meta:
        model = VaccinationRecord
        fields = ['user_id', 'vaccine_brand', 'vaccine_description', 'vaccinated_at']
