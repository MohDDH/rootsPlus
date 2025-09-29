# resources.py
from import_export import resources
from .models import FarmReport

class FarmReportResource(resources.ModelResource):
    class Meta:
        model = FarmReport
        fields = (
            'farm__name',
            'season',
            'generated_at',
            'overall_score',
            'status',
            'author__name',
            'summary',
            'recommendations',
            'notes',
        )