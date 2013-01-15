# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Feature_Type'
        db.create_table('hippo_feature_type', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('hippo', ['Feature_Type'])

        # Adding model 'Feature'
        db.create_table('hippo_feature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Feature_Type'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('sequence', self.gf('django.db.models.fields.TextField')()),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('cut_after', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('hippo', ['Feature'])

        # Adding unique constraint on 'Feature', fields ['name', 'hash']
        db.create_unique('hippo_feature', ['name', 'hash'])

        # Adding model 'Feature_Database'
        db.create_table('hippo_feature_database', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('last_built', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('hippo', ['Feature_Database'])

        # Adding M2M table for field features on 'Feature_Database'
        db.create_table('hippo_feature_database_features', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feature_database', models.ForeignKey(orm['hippo.feature_database'], null=False)),
            ('feature', models.ForeignKey(orm['hippo.feature'], null=False))
        ))
        db.create_unique('hippo_feature_database_features', ['feature_database_id', 'feature_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Feature', fields ['name', 'hash']
        db.delete_unique('hippo_feature', ['name', 'hash'])

        # Deleting model 'Feature_Type'
        db.delete_table('hippo_feature_type')

        # Deleting model 'Feature'
        db.delete_table('hippo_feature')

        # Deleting model 'Feature_Database'
        db.delete_table('hippo_feature_database')

        # Removing M2M table for field features on 'Feature_Database'
        db.delete_table('hippo_feature_database_features')


    models = {
        'hippo.feature': {
            'Meta': {'ordering': "('type', 'name')", 'unique_together': "(('name', 'hash'),)", 'object_name': 'Feature'},
            'cut_after': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'sequence': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature_Type']"})
        },
        'hippo.feature_database': {
            'Meta': {'object_name': 'Feature_Database'},
            'features': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hippo.Feature']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_built': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'hippo.feature_type': {
            'Meta': {'object_name': 'Feature_Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['hippo']