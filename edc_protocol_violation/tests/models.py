from django.contrib import admin
from django.db import models
from edc_model.models import BaseUuidModel
from edc_utils import get_utcnow


class TestModel(models.Model):

    f1 = models.CharField(max_length=10, null=True)

    class Meta:
        verbose_name = "Test Model"


admin.site.register(TestModel)


class Prn(BaseUuidModel):

    subject_identifier = models.CharField(max_length=50, null=True, blank=True)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)

    class Meta(BaseUuidModel.Meta):
        pass
