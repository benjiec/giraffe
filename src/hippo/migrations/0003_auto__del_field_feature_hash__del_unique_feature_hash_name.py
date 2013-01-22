# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Feature', fields ['hash', 'name']
        db.delete_unique('hippo_feature', ['hash', 'name'])

        # Deleting field 'Feature.hash'
        db.delete_column('hippo_feature', 'hash')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Feature.hash'
        raise RuntimeError("Cannot reverse this migration. 'Feature.hash' and its values cannot be restored.")
        # Adding unique constraint on 'Feature', fields ['hash', 'name']
        db.create_unique('hippo_feature', ['hash', 'name'])


    models = {
        'hippo.feature': {
            'Meta': {'ordering': "('type', 'name')", 'object_name': 'Feature'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'sequence': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature_Type']"})
        },
        'hippo.feature_database': {
            'Meta': {'object_name': 'Feature_Database'},
            'features': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['hippo.Feature']", 'null': 'True', 'blank': 'True'}),
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