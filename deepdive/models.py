from django.db import models

from djangotoolbox.fields import ListField
from djangotoolbox.fields import EmbeddedModelField
from djangotoolbox.fields import DictField
from django_mongodb_engine.contrib import MongoDBManager
from django import forms


def get_tag_options(proc_type):
    choices_list=[]
    if proc_type == "OCR":
        processings = OcrProcessing.objects.using('processings').filter()
    elif proc_type == "NLP":
        processings = NlpProcessing.objects.using('processings').filter()
    else:
        return choices_list
    for proc in processings:
        choices_list.append( (proc.tag, proc.tag) )
    return choices_list

class ProcForm(forms.Form):
    def __init__(self, proctype="OCR", *args, **kwargs):
        super(ProcForm, self).__init__(*args, **kwargs)
        self.fields['tag'] = forms.ChoiceField(
                choices=get_tag_options(proctype) )

class Article(models.Model):
    class Meta:
        db_table = 'articles'
    title = models.CharField(max_length = 1024, null=True)
    pubname = models.CharField(max_length = 256, null=True)
    sha1 = models.CharField(max_length = 32, null=True)
    vol = models.CharField(max_length = 32, null=True)
    issue = models.CharField(max_length = 32, null=True)
    startingPage = models.CharField(max_length = 32, null=True)
    endingPage = models.CharField(max_length = 32, null=True)
    URL = models.CharField(max_length = 256, null=True)
    ocr_processing = DictField(null=True)
    nlp_processing = DictField(null=True)
    cuneiform_processing = DictField(null=True)
    fonttype_processing = DictField(null=True)
    objects = MongoDBManager()

class NlpProcessing(models.Model):
    tag = models.CharField(max_length = 256)
    type = models.CharField(max_length = 64)
    comments = models.CharField(max_length = 1024)
    binaries = DictField()
    jobs = ListField()
    class Meta:
        db_table = "nlp_processing"

class OcrProcessing(models.Model):
    tag = models.CharField(max_length = 256)
    type = models.CharField(max_length = 64)
    comments = models.CharField(max_length = 1024)
    binaries = DictField()
    jobs = ListField()
    class Meta:
        db_table = "ocr_processing"

class Metric(models.Model):
    metrics = DictField(null=True)
    time = models.DateTimeField(null=True)
    objects = MongoDBManager()
    class Meta:
        abstract = True

class HourMetric(Metric):
    class Meta:
        db_table="hour_view"

class DayMetric(Metric):
    class Meta:
        db_table="day_view"

class WeekMetric(Metric):
    class Meta:
        db_table="week_view"

class MonthMetric(Metric):
    class Meta:
        db_table="month_view"

class Publication(models.Model):
    title = models.CharField(max_length=256)
#    id = models.CharField()
    downloaded = models.IntegerField()
    ocr_versions = DictField()
    nlp_versions = DictField()
    class Meta:
        db_table = 'journals_test'
