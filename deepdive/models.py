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
#    id = models.CharField()
    title = models.CharField(max_length = 1024)
    pubname = models.CharField(max_length = 256)
    sha1 = models.CharField(max_length = 32)
    class Meta:
        db_table = 'articles'
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

class Publication(models.Model):
    title = models.CharField(max_length=256)
#    id = models.CharField()
    downloaded = models.IntegerField()
    ocr_versions = DictField()
    nlp_versions = DictField()
    class Meta:
        db_table = 'journals_test'
