import pdb
from deepdive.models import Publication, Article, NlpProcessing, OcrProcessing,ProcForm, HourMetric, DayMetric, WeekMetric, MonthMetric
from rest_framework import serializers

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'pubname', 'sha1', 'vol', 'startingPage', 'endingPage', 'issue',
                'URL', 'ocr_processing', 'nlp_processing','cuneiform_processing', 'fonttype_processing')

class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('time','metrics')

class HourSerializer(MetricSerializer):
    class Meta(MetricSerializer.Meta):
        model = HourMetric
class DaySerializer(MetricSerializer):
    class Meta(MetricSerializer.Meta):
        model = DayMetric
class WeekSerializer(MetricSerializer):
    class Meta(MetricSerializer.Meta):
        model = WeekMetric
class MonthSerializer(MetricSerializer):
    class Meta(MetricSerializer.Meta):
        model = MonthMetric
