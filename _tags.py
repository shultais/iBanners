# -*- coding: utf-8 -*-

from django import template
from django.utils.encoding import smart_str
from django.core.urlresolvers import get_callable, RegexURLResolver, get_resolver
from django.template import Node, NodeList, TextNode, TemplateSyntaxError, Library, resolve_variable
from ibanners.models import Zone, Banner, Campaign
from settings import MEDIA_URL
import re, os, random
from datetime import datetime as dt
from django.db.models import Q

class BannerNode(template.Node):
   def __init__(self, request, zone_id):
      self.request = request
      self.zone_id = zone_id
   def render(self, context):
      pr = {1:3,2:5,3:7,4:9,5:11,6:13,7:15,8:17,9:20}
      probabilities = []

      try:
         zone = Zone.objects.get(id=self.zone_id)
      except:
         zone = None
      if zone:
         banners = Banner.objects.filter(
            (Q(begin_date__lte=dt.now()) | Q(begin_date__isnull=True)),
            (Q(end_date__gte=dt.now()) | Q(end_date__isnull=True)),
            zones=zone).order_by('-campaign__priority')
         count = banners.count()

         banner = False
         hbanner = u""

         if count == 1:
            banner = banners[0]
         elif count > 1:
            url = ""
            # Поиск самого крутого баннера в зоне, в зависимости от самой крутой кампании
            for b in banners:
               if ((b.shows < b.max_shows) or (b.max_shows == 0)) and ((b.clicks < b.max_clicks) or (b.max_clicks == 0)):
                  if int(b.campaign.priority) == 10:
                     banner = b
                     break
            # Если крутой баннер не найден, то ищем простые баннеры, исключая собственные кампании
            if not banner:
               banners2 = banners.exclude(campaign__priority=0)
               # Если такие банеры есть строим полосу вероятностей
               if banners2.count() > 0:
                  for b in banners2:
                     if ((b.shows < b.max_shows) or (b.max_shows == 0)) and ((b.clicks < b.max_clicks) or (b.max_clicks == 0)):
                        for x in range(pr[b.campaign.priority]):
                           probabilities.append(b.campaign.priority)
                  priority = random.choice(probabilities)
                  banners2 = Banner.objects.filter(
                     (Q(begin_date__lte=dt.now()) | Q(begin_date__isnull=True)),
                     (Q(end_date__gte=dt.now()) | Q(end_date__isnull=True)),
                     zones=zone,campaign__priority=priority).order_by('-campaign__priority')
                  # Если в вероятность попал один баннер
                  if banners2.count() == 1:
                     banner = banners2[0]
                  # Если в вероятность попало более одного баннера, то выбираем из равновероятного
                  elif banners2.count() > 1:
                     bids = []
                     for b in banners2:
                        if ((b.shows < b.max_shows) or (b.max_shows == 0)) and ((b.clicks < b.max_clicks) or (b.max_clicks == 0)):
                           bids.append(b.id)
                     bid = random.choice(bids)
                     banner = banners2.get(id=bid)
                  else:
                     pass
            # На данном этапе остались только собственные кампании
            if not banner:
               bids = []
               for b in banners:
                  if ((b.shows < b.max_shows) or (b.max_shows == 0)) and ((b.clicks < b.max_clicks) or (b.max_clicks == 0)):
                     bids.append(b.id)
               bid = random.choice(bids)
               banner = banners.get(id=bid)
   
         # Если баннер всё-таки найден
         if banner:
            banner.shows = banner.shows + 1
            banner.save()
            url = u"%sbanners/%s" % (MEDIA_URL, os.path.basename(banner.file.path))
            #print banner.file
   
            code = u""
            # flash баннеры
            if banner.banner_type == 'f':
               code = u"""<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=5,0,0,0" width="%s" height="%s">
               <param name=movie value="%s">
               <param name=quality value=high>
               <embed src="%s?banner_href=/banners/%s/" quality=high pluginspage="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash" type="application/x-shockwave-flash" width="%s" height="%s"></embed>
               </object>""" % (banner.width, banner.height, url, url, banner.id ,banner.width, banner.height)
            # графические баннеры
            elif banner.banner_type == 'g':
               code = """<img src="%s" alt="%s"/>""" % (url,banner.alt)
            # html баннеры
            elif banner.banner_type == 'h':
               pass
            hbanner = u"""<div style="width:%spx;height:%spx;">%s</div>""" % (banner.width,banner.height, code)
         else:
            pass
         return hbanner
      # Если зона не найдена
      else:
         return u""

# Тег для загрузки баннеров
def do_banner(parser, token):
   try:
      tag_name, request, zone_id = token.split_contents()
   except ValueError:
      raise template.TemplateSyntaxError, "%r tag requires a two arguments" % token.contents.split()[0]
   return BannerNode(request, zone_id)

register = template.Library()
register.tag('banner', do_banner)