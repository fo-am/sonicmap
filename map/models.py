from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth.models import User

class Tag(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=64)
	alias = models.CharField(max_length=64)
	description = models.TextField()

	def __repr__ (self):
		return self.alias

	def __str__ (self):
		return self.alias

class Event(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=64)
	event_date = models.DateField(auto_now=False, auto_now_add=False)
	center_lat = models.FloatField()
	center_long = models.FloatField()
	zoom_level = models.IntegerField()

	def __repr__(self):
		return '<Event %s>' % self.name

	def __str__(self):
		return self.name

	class Meta:
		managed = True

class Zone(gismodels.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=64)
	geom = gismodels.GeometryCollectionField(spatial_index=True)
	colour = models.CharField(max_length=7)
	event = models.ForeignKey(Event, related_name='zones', null=True, blank=True, default = None)
	objects = gismodels.GeoManager()
	author = models.ForeignKey(User, related_name='zones', null=True, blank=True, default=None)

	def __repr__ (self):
		return '<Zone %s>' % self.name

	def __str__ (self):
		return self.name

	class Meta:
		managed = True

class ZoneTag(models.Model):
	id = models.AutoField(primary_key=True)
	zone = models.ForeignKey(Zone, related_name='zonetag')
	tag = models.ForeignKey(Tag, related_name='zonetag')
	date = models.DateTimeField(auto_now=True)


# Create your models here.
