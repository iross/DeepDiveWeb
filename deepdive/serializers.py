from deepdive.models import Publication, Article, NlpProcessing, OcrProcessing,ProcForm
from rest_framework import serializers

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'pubname', 'sha1', 'vol', 'startingPage', 'endingPage', 'issue',
                'URL', 'ocr_processing', 'nlp_processing','cuneiform_processing', 'fonttype_processing')
