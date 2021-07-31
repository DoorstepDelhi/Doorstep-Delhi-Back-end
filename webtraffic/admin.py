from django.contrib import admin
import nested_admin

from .models import Website, WebsiteHit


class WebsiteAdmin(nested_admin.NestedModelAdmin):
    inlines = []
    list_display = [
                    'id',
                    'name',
                    'url',
                    'timer',
                    'user',
                    'category',
                    ]
    list_editable = [
                    'category',
                    ]
    list_display_links = [
                    'id',
                    'name',
                    'url',
                    'timer',
                    'user',
                    ]
    list_filter = [
                    'category',
                    'status',
                    'traffic_source',
                    'high_quality',
                    ]
    search_fields = [
                    'name',
                    'url',
                    ]


class WebsiteHitAdmin(nested_admin.NestedModelAdmin):
    inlines = []
    list_display = [
                    'id',
                    'website',
                    'user',
                    'type',
                    'created_at',
                    ]
    list_display_links = [
                    'id',
                    'website',
                    'user',
                    'type',
                    'created_at',
                    ]
    list_filter = [
                    'type',
                    ]
    search_fields = [
                    'website',
                    ]


admin.site.register(Website, WebsiteAdmin)
admin.site.register(WebsiteHit, WebsiteHitAdmin)
