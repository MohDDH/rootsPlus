from django.contrib import admin
from .models import Farm, User, Agronomist, Activity, Analysis, Evaluation, Crop  # لاحظ حذف FarmReport هنا
from import_export.admin import ExportMixin
from .resources import FarmReportResource
from .models import FarmReport  # سجلناه هنا بشكل منفصل

# تسجيل باقي الموديلات
admin.site.register(Farm)
admin.site.register(User)
admin.site.register(Agronomist)
admin.site.register(Activity)
admin.site.register(Analysis)
admin.site.register(Evaluation)
admin.site.register(Crop)

# تسجيل FarmReport بتخصيص كامل
@admin.register(FarmReport)
class FarmReportAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = FarmReportResource
    list_display = ('farm_name', 'season', 'generated_at', 'overall_score', 'status', 'author_name')
    search_fields = ('farm__name', 'season', 'author__name', 'status')
    list_filter = ('season', 'status', 'generated_at')
    readonly_fields = ('summary', 'generated_at')

    def farm_name(self, obj):
        return obj.farm.name
    def author_name(self, obj):
        return obj.author.name if obj.author else "N/A"