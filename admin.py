# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from iBanners.models import Zone, Client, Banner, Campaign

class ZoneAdmin(admin.ModelAdmin):
   list_display = ('get_site','id','name','description','price')
   list_filter = ('site',)

class ClientAdmin(admin.ModelAdmin):
   list_per_page = 30
   list_display = ('name','contact','email')
   search_fields = ('name','contact')

class BannerAdmin(admin.ModelAdmin):
   list_per_page = 30
   list_display = ('id', 'name','campaign','get_banner_zones','banner_type','shows','clicks','ctr')
   raw_id_fields = ('campaign',)
   fieldsets = (
      (u"Базовые настройки", {
         'classes': ('wide',),
         'fields': ('campaign','zones','banner_type', 'name','foreign_url','comment')
      }),
      (u"Баннер", {
         'classes': ('wide',),
         'fields': ('swf_file','img_file','alt','html_text')
      }),
      (u"Размеры", {
         'classes': ('wide'),
         'fields': ('width', 'height')
      }),
      (u"Статистика", {
         'classes': ('wide',),
         'fields': ('clicks','shows')
      }),
      (u"Ограничения", {
         'classes': ('wide',),
         'fields': ('max_clicks','max_shows','begin_date','end_date','var')
      }),
   )
   search_fields = ('name','campaign__name','campaign__client__name', 'comment', 'html_text')
   list_display_links = ('name',)


class CampaignAdmin(admin.ModelAdmin):
   list_display = ('client','name','priority','begin_date','end_date')
   list_filter = ('priority',)
   search_fields = ('client__name', 'name')
   date_hierarchy = 'end_date'
   raw_id_fields = ('client',)

class XCampaignAdmin(admin.ModelAdmin):
   list_display = ('client','name','priority','begin_date','end_date')
   list_filter = ('priority',)


admin.site.register(Zone, ZoneAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Campaign, CampaignAdmin)
