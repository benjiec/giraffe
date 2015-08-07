from django.core.exceptions import PermissionDenied
from django.contrib import admin
import models

class FeatureAdmin(admin.ModelAdmin):

    def sequence(obj):
        return '%s bps' % len(obj.sequence)

    list_display = ('id', 'name', 'dna_or_protein', 'type', sequence, 'last_modified')
    list_filter = ('type', 'feature_database')
    search_fields = ('name',)

admin.site.register(models.Feature, FeatureAdmin)


class FeatureDatabaseAdmin(admin.ModelAdmin):

    def has_delete_permission(self, *args, **kwargs):
        return False

    def delete_view(self, request, object_id, extra_context=None):
        raise PermissionDenied

    fields = ('name', 'features')
    filter_horizontal = ('features',)

admin.site.register(models.Feature_Database, FeatureDatabaseAdmin)
