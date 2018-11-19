# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('event_date', models.DateField()),
                ('center_lat', models.FloatField()),
                ('center_long', models.FloatField()),
                ('zoom_level', models.IntegerField()),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('alias', models.CharField(max_length=64)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('geom', django.contrib.gis.db.models.fields.GeometryCollectionField(srid=4326)),
                ('colour', models.CharField(max_length=7)),
                ('author', models.ForeignKey(related_name='zones', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('event', models.ForeignKey(related_name='zones', default=None, blank=True, to='map.Event', null=True)),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ZoneTag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('tag', models.ForeignKey(related_name='zonetag', to='map.Tag')),
                ('zone', models.ForeignKey(related_name='zonetag', to='map.Zone')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
