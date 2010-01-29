# -*- coding: utf-8 -*-

import re, os, random
from datetime import datetime as dt

from django import template
from django.utils.encoding import smart_str
from django.core.urlresolvers import get_callable, RegexURLResolver, get_resolver
from django.template import Node, NodeList, TextNode, TemplateSyntaxError, Library, resolve_variable
from django.db.models import Q

from settings import MEDIA_URL, SITE_URL
from iBanners.models import Zone, Banner, Campaign
from iBanners.views import gen_banner_code

class BannerNode(template.Node):
   def __init__(self, request, zone_id, var):
      self.request = template.Variable(request)
      self.zone_id = zone_id

      if var:
         try:
            self.var = template.Variable(var)
         except:
            self.var = False
      else: self.var = False

   def render(self, context):
      if self.var:
         self.var = str(self.var.resolve(context))
      return gen_banner_code(self.request.resolve(context), self.zone_id, self.var)

# Тег для загрузки баннеров
def do_banner(parser, token):
   try:
      tokens = token.split_contents()
      if tokens.__len__() == 3:
         tag_name, request, zone_id = token.split_contents()
         var = False
      elif tokens.__len__() == 4:
         tag_name, request, zone_id,var = token.split_contents()
   except ValueError:
      raise template.TemplateSyntaxError, "%r tag requires a 2 or 3 arguments" % token.contents.split()[0]
   return BannerNode(request, zone_id, var)

register = template.Library()
register.tag('banner', do_banner)
