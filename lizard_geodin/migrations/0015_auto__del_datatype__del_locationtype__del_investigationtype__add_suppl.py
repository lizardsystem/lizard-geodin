# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'DataType'
        db.delete_table('lizard_geodin_datatype')

        # Deleting model 'LocationType'
        db.delete_table('lizard_geodin_locationtype')

        # Deleting model 'InvestigationType'
        db.delete_table('lizard_geodin_investigationtype')

        # Adding model 'Supplier'
        db.create_table('lizard_geodin_supplier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('lizard_geodin', ['Supplier'])

        # Adding model 'Parameter'
        db.create_table('lizard_geodin_parameter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('lizard_geodin', ['Parameter'])

        # Deleting field 'Measurement.location_type'
        db.delete_column('lizard_geodin_measurement', 'location_type_id')

        # Deleting field 'Measurement.data_type'
        db.delete_column('lizard_geodin_measurement', 'data_type_id')

        # Deleting field 'Measurement.investigation_type'
        db.delete_column('lizard_geodin_measurement', 'investigation_type_id')

        # Adding field 'Measurement.location_type_name'
        db.add_column('lizard_geodin_measurement', 'location_type_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'Measurement.investigation_type_name'
        db.add_column('lizard_geodin_measurement', 'investigation_type_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'Measurement.data_type_name'
        db.add_column('lizard_geodin_measurement', 'data_type_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'Measurement.supplier'
        db.add_column('lizard_geodin_measurement', 'supplier', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'measurements', null=True, to=orm['lizard_geodin.Supplier']), keep_default=False)

        # Adding field 'Measurement.parameter'
        db.add_column('lizard_geodin_measurement', 'parameter', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'measurements', null=True, to=orm['lizard_geodin.Parameter']), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'DataType'
        db.create_table('lizard_geodin_datatype', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('lizard_geodin', ['DataType'])

        # Adding model 'LocationType'
        db.create_table('lizard_geodin_locationtype', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('lizard_geodin', ['LocationType'])

        # Adding model 'InvestigationType'
        db.create_table('lizard_geodin_investigationtype', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('lizard_geodin', ['InvestigationType'])

        # Deleting model 'Supplier'
        db.delete_table('lizard_geodin_supplier')

        # Deleting model 'Parameter'
        db.delete_table('lizard_geodin_parameter')

        # Adding field 'Measurement.location_type'
        db.add_column('lizard_geodin_measurement', 'location_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'measurements', null=True, to=orm['lizard_geodin.LocationType'], blank=True), keep_default=False)

        # Adding field 'Measurement.data_type'
        db.add_column('lizard_geodin_measurement', 'data_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'measurements', null=True, to=orm['lizard_geodin.DataType'], blank=True), keep_default=False)

        # Adding field 'Measurement.investigation_type'
        db.add_column('lizard_geodin_measurement', 'investigation_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'measurements', null=True, to=orm['lizard_geodin.InvestigationType'], blank=True), keep_default=False)

        # Deleting field 'Measurement.location_type_name'
        db.delete_column('lizard_geodin_measurement', 'location_type_name')

        # Deleting field 'Measurement.investigation_type_name'
        db.delete_column('lizard_geodin_measurement', 'investigation_type_name')

        # Deleting field 'Measurement.data_type_name'
        db.delete_column('lizard_geodin_measurement', 'data_type_name')

        # Deleting field 'Measurement.supplier'
        db.delete_column('lizard_geodin_measurement', 'supplier_id')

        # Deleting field 'Measurement.parameter'
        db.delete_column('lizard_geodin_measurement', 'parameter_id')


    models = {
        'lizard_geodin.apistartingpoint': {
            'Meta': {'object_name': 'ApiStartingPoint'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'lizard_geodin.measurement': {
            'Meta': {'object_name': 'Measurement'},
            'data_type_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigation_type_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'location_type_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'parameter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'measurements'", 'null': 'True', 'to': "orm['lizard_geodin.Parameter']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'measurements'", 'null': 'True', 'to': "orm['lizard_geodin.Project']"}),
            'supplier': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'measurements'", 'null': 'True', 'to': "orm['lizard_geodin.Supplier']"})
        },
        'lizard_geodin.measurementconfiguration': {
            'Meta': {'object_name': 'MeasurementConfiguration'},
            'flot_fields': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'measurement_configurations'", 'null': 'True', 'to': "orm['lizard_geodin.Measurement']"}),
            'metadata_filter': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'lizard_geodin.parameter': {
            'Meta': {'object_name': 'Parameter'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'lizard_geodin.point': {
            'Meta': {'object_name': 'Point'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'measurement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'points'", 'null': 'True', 'to': "orm['lizard_geodin.Measurement']"}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'lizard_geodin.supplier': {
            'Meta': {'object_name': 'Supplier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['lizard_geodin']
