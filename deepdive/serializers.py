from deepdive.models import Publication, Article, NlpProcessing, OcrProcessing,ProcForm
from rest_framework import serializers

class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'pubname', 'sha1')
