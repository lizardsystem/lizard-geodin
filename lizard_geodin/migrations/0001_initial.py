# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Project'
        db.create_table('lizard_geodin_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('lizard_geodin', ['Project'])

        # Adding model 'LocationType'
        db.create_table('lizard_geodin_locationtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'location_types', null=True, to=orm['lizard_geodin.Project'])),
        ))
        db.send_create_signal('lizard_geodin', ['LocationType'])

        # Adding model 'InvestigationType'
        db.create_table('lizard_geodin_investigationtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('location_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'investigation_types', null=True, to=orm['lizard_geodin.LocationType'])),
        ))
        db.send_create_signal('lizard_geodin', ['InvestigationType'])

        # Adding model 'DataType'
        db.create_table('lizard_geodin_datatype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('investigation_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'data_types', null=True, to=orm['lizard_geodin.InvestigationType'])),
        ))
        db.send_create_signal('lizard_geodin', ['DataType'])


    def backwards(self, orm):
        
        # Deleting model 'Project'
        db.delete_table('lizard_geodin_project')

        # Deleting model 'LocationType'
        db.delete_table('lizard_geodin_locationtype')

        # Deleting model 'InvestigationType'
        db.delete_table('lizard_geodin_investigationtype')

        # Deleting model 'DataType'
        db.delete_table('lizard_geodin_datatype')


    models = {
        'lizard_geodin.datatype': {
            'Meta': {'object_name': 'DataType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigation_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'data_types'", 'null': 'True', 'to': "orm['lizard_geodin.InvestigationType']"}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_geodin.investigationtype': {
            'Meta': {'object_name': 'InvestigationType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'investigation_types'", 'null': 'True', 'to': "orm['lizard_geodin.LocationType']"}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_geodin.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'location_types'", 'null': 'True', 'to': "orm['lizard_geodin.Project']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_geodin.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['lizard_geodin']
