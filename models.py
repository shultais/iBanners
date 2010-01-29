# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.sites.models import Site
from settings import MEDIA_ROOT, MEDIA_URL

BANNERS_TYPE = (
   ('g',u'графический баннер'),
   ('f',u'Flash-баннер'),
   ('h',u'HTML-баннер'),
)


PRIORITY = (
   (10,u'Эксклюзивный'),
   (9,u'Максимально высокий'),
   (8,u'Очень высокий'),
   (7,u'Высокий'),
   (6,u'Выше среднего'),
   (5,u'Средний'),
   (4,u'Ниже среднего'),
   (3,u'Низкий'),
   (2,u'Очень низкий'),
   (1,u'Максимально низкий'),
   (0,u'Собственные кампании'),
)

class Zone(models.Model):
   site = models.ForeignKey(Site,verbose_name=u"сайт",)
   name = models.CharField(max_length=50,verbose_name=u"название")
   description = models.CharField(max_length=255,verbose_name=u"описание")
   price = models.IntegerField(verbose_name=u"Цена месяца показа")
   html_after_banner = models.CharField(max_length=255,verbose_name=u"HTML после баннера",blank=True,default="")
   html_pre_banner = models.CharField(max_length=255,verbose_name=u"HTML перед баннером",blank=True,default="")

   class Meta:
      ordering = ["site","id"]
      verbose_name = u"""зона"""
      verbose_name_plural = u"""зоны"""

   def get_site(self):
      return u"%s [%s]" % (self.site.name, self.site)
   get_site.short_description = u'Сайт'

   def __unicode__(self):
      return u"%s: %s %s" % (self.site.name, self.name, self.description)

class Client(models.Model):
   name = models.CharField(max_length=100,verbose_name=u"Имя")
   contact = models.CharField(max_length=100,verbose_name=u"Контакт")
   email = models.EmailField(max_length=100,verbose_name=u"E-mail")
   one_banner_per_page = models.BooleanField(default=True,blank=True,verbose_name=u"Показывать только один баннер этого рекламодателя на странице")

   class Meta:
      ordering = ["name",]
      verbose_name = u"""клиент"""
      verbose_name_plural = u"""клиенты"""

   def __unicode__(self):
      return self.name

class Campaign(models.Model):
   client = models.ForeignKey(Client,verbose_name=u"Клиент")
   name = models.CharField(max_length=100,verbose_name=u"Название")
   begin_date = models.DateTimeField(verbose_name=u"Дата активации",null=True,blank=True,help_text=u"Оставьте поле пустым, чтобы немедленно активировать кампанию")
   end_date = models.DateTimeField(verbose_name=u"Дата деактивации",null=True,blank=True,help_text=u"Оставьте поле пустым, чтобы кампания была активна всегда")
   priority = models.IntegerField(verbose_name=u"Приоритет",choices=PRIORITY)

   class Meta:
      ordering = ["client__name", "name",]
      verbose_name = u"""кампания"""
      verbose_name_plural = u"""кампания"""

   def __unicode__(self):
      return u"%s - %s" % (self.client.name, self.name)

class Banner(models.Model):
   campaign = models.ForeignKey(Campaign,verbose_name=u"Кампания")
   zones = models.ManyToManyField(Zone,verbose_name=u"Связанные зоны")
   banner_type = models.CharField(max_length=1,verbose_name=u"Тип баннера",choices=BANNERS_TYPE)
   name = models.CharField(max_length=100,blank=False,verbose_name=u"Название")
   foreign_url = models.CharField(max_length=200,blank=True,verbose_name=u"URL перехода",default="") # Внешний URL куда ведет баннер
   width = models.CharField(
      blank=True, default="", null=False, verbose_name=u"Ширина",max_length=100, help_text=u"После значения указывайте единицы, например px или %")
   height = models.CharField(
      blank=True, null=False, default="",verbose_name=u"Высота",max_length=100, help_text=u"После значения указывайте единицы, например px или %")
   # Статистика
   clicks = models.PositiveIntegerField(blank=True,verbose_name=u"Кликов",default=0) # Число кликов
   shows  = models.PositiveIntegerField(blank=True,verbose_name=u"Показов",default=0) # Число показов
   # Ограничения
   max_clicks = models.PositiveIntegerField(blank=True,verbose_name=u"Лимит кликов", default=0, null=False, help_text=u"0 - лимит не ограничен")
   max_shows  = models.PositiveIntegerField(blank=True,verbose_name=u"Лимит показов",default=0,null=False,help_text=u"0 - лимит не ограничен")
   begin_date = models.DateTimeField(null=True,blank=True,verbose_name=u"Дата начала")
   end_date = models.DateTimeField(null=True,blank=True,verbose_name=u"Дата окончания")
   # Прорабатываем баннеры
   swf_file = models.FileField(upload_to=MEDIA_ROOT+"/ibas/swf/",blank=True,verbose_name=u"Путь до SWF файла",help_text=u"Только для Flash баннеров",null=True)
   img_file = models.FileField(upload_to=MEDIA_ROOT+"/ibas/img/",blank=True,verbose_name=u"Путь до графического файла",help_text=u"Использовать для графических баннеров и для замены Flash баннеров в случае отсутствия у пользователя flash-плеера",null=True)
   alt = models.CharField(max_length=100,blank=True,verbose_name=u"alt текст",default="")
   comment = models.TextField(max_length=255,blank=True,verbose_name=u"Комментарий",default="")
   html_text = models.TextField(blank=True,null=False,default="",verbose_name=u"HTML текст")
   var = models.CharField(max_length=255,verbose_name=u"Переменная",blank=True,default="",null=True)

   class Meta:
      ordering = ["campaign__client__name",]
      verbose_name = u"""баннер"""
      verbose_name_plural = u"""баннеры"""

   def get_size(self):
      return u"%sx%s" % (self.width, self.height)
   get_size.short_description = u'Размеры'

   def get_banner_zones(self):
      htzones = "<ul>"
      for zone in self.zones.all():
         htzones += "<li>%s [%s] - %s</li>" % (zone.site, zone.name, zone.description)
      htzones += "</ul>"
      return htzones
   get_banner_zones.short_description = u'Зоны'
   get_banner_zones.allow_tags = True

   def get_campaign_satus(self):
      print dir(self.campaign)
      return "%s - %s" % (self.campaign.priority, self.campaign.get_priority_display())
   get_campaign_satus.short_description = u'Статус кампании'
   get_campaign_satus.allow_tags = True

   def ctr(self):
      if self.shows != 0:
         c = str(float(self.clicks)/float(self.shows)*100.)
         return c[:c.rfind('.')+3]
      else:
         return u"-"
   ctr.short_description = u'CTR'

   def __unicode__(self):
      return self.name