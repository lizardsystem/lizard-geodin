# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Measurement.location_type_name'
        db.alter_column('lizard_geodin_measurement', 'location_type_name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

        # Changing field 'Measurement.data_type_name'
        db.alter_column('lizard_geodin_measurement', 'data_type_name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

        # Changing field 'Measurement.investigation_type_name'
        db.alter_column('lizard_geodin_measurement', 'investigation_type_name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

        # Changing field 'ApiStartingPoint.name'
        db.alter_column('lizard_geodin_apistartingpoint', 'name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

        # Changing field 'Point.name'
        db.alter_column('lizard_geodin_point', 'name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))

        # Changing field 'Project.name'
        db.alter_column('lizard_geodin_project', 'name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True))


    def backwards(self, orm):
        
        # Changing field 'Measurement.location_type_name'
        db.alter_column('lizard_geodin_measurement', 'location_type_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'Measurement.data_type_name'
        db.alter_column('lizard_geodin_measurement', 'data_type_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'Measurement.investigation_type_name'
        db.alter_column('lizard_geodin_measurement', 'investigation_type_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'ApiStartingPoint.name'
        db.alter_column('lizard_geodin_apistartingpoint', 'name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'Point.name'
        db.alter_column('lizard_geodin_point', 'name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'Project.name'
        db.alter_column('lizard_geodin_project', 'name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))


    models = {
        'lizard_geodin.apistartingpoint': {
            'Meta': {'object_name': 'ApiStartingPoint'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'lizard_geodin.measurement': {
            'Meta': {'ordering': "[u'project', u'supplier', u'name']", 'object_name': 'Measurement'},
            'data_type_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigation_type_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'location_type_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'parameter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'measurements'", 'null': 'True', 'to': "orm['lizard_geodin.Parameter']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'measurements'", 'null': 'True', 'to': "orm['lizard_geodin.Project']"}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'measurements'", 'null': 'True', 'to': "orm['lizard_geodin.Supplier']"})
        },
        'lizard_geodin.parameter': {
            'Meta': {'object_name': 'Parameter'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'lizard_geodin.point': {
            'Meta': {'ordering': "(u'name', u'slug')", 'object_name': 'Point'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'measurement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'points'", 'null': 'True', 'to': "orm['lizard_geodin.Measurement']"}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'x': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'lizard_geodin.project': {
            'Meta': {'ordering': "(u'-active', u'name')", 'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'api_starting_point': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'location_types'", 'null': 'True', 'to': "orm['lizard_geodin.ApiStartingPoint']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'lizard_geodin.supplier': {
            'Meta': {'object_name': 'Supplier'},
            'html_color': ('django.db.models.fields.CharField', [], {'default': "u'#444444'", 'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['lizard_geodin']
