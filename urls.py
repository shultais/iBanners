# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

#urlpatterns += patterns('ibanners.views',     url(regex=r'^banners/(?P<banner_id>\d+)/$',   view='banner', name='ibanners.banner'))

urlpatterns = patterns('iBanners.views',
   url(
      regex = r'^(?P<banner_id>\d+)/$',
      view  = 'banner',
      name  = 'ibanners.banner'),
   url(
      regex = r'^zones/(?P<zone_id>\d+)/$',
      view  = 'zones',
      name  = 'ibanners.zones'),
)