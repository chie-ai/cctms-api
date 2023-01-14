from django.db import models
from bnhs_users.models import BNHSUser, TimeStampedModel
import datetime

class CovidCaseRecord(TimeStampedModel):
    SUSPECT_COVID19_CASE = 'suspect covid-19 case'
    PROBABLE_COVID19_CASE = 'probable covid-19 case'
    CONFIRMED_COVID19_CASE = 'confirmed covid-19 case'
    RECOVERED_COVID19_CASE = 'recovered covid-19 case'
    UNINFECTED_COVID19_CASE = 'uninfected covid-19 case'

    CLASSIFICATION = (
        (SUSPECT_COVID19_CASE, SUSPECT_COVID19_CASE),
        (PROBABLE_COVID19_CASE, PROBABLE_COVID19_CASE),
        (CONFIRMED_COVID19_CASE, CONFIRMED_COVID19_CASE),
        (RECOVERED_COVID19_CASE, RECOVERED_COVID19_CASE),
        (UNINFECTED_COVID19_CASE, UNINFECTED_COVID19_CASE)
    )

    MILD = 'mild disease'
    MODERATE = 'moderate disease'
    SEVERE = 'severe disease'

    SEVERITY = (
        (MILD, MILD),
        (MODERATE, MODERATE),
        (SEVERE, SEVERE)
    )
    user = models.ForeignKey(BNHSUser, on_delete=models.CASCADE, unique=False, related_name='covid19_status')
    classification = models.CharField(max_length=255, choices=CLASSIFICATION, default=UNINFECTED_COVID19_CASE)
    severity = models.CharField(max_length=255, choices=SEVERITY, blank=True, default='')

    # class Meta:
    #     ordering: ['-created_at']

    def __str__(self):
        return self.classification

class VaccinationRecord(models.Model):
    user = models.ForeignKey(BNHSUser, on_delete=models.CASCADE, related_name='vaccination_record')
    vaccine_brand = models.CharField(max_length=255, blank=True, default='')
    vaccine_description = models.CharField(max_length=255, blank=True, default='')
    vaccinated_at = models.DateField()

    def __str__(self):
        return self.vaccine_brand
