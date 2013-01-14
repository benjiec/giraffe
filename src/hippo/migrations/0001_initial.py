# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sequence_Feature'
        db.create_table('hippo_sequence_feature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sequence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Sequence'])),
            ('start', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('end', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('clockwise', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feature_db_index', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Feature_DB_Index'])),
            ('subset_start', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('subset_end', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('is_variant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_gaps', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('hippo', ['Sequence_Feature'])

        # Adding model 'Sequence'
        db.create_table('hippo_sequence', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sequence', self.gf('django.db.models.fields.TextField')()),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('db', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Feature_Database'])),
            ('db_version', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('hippo', ['Sequence'])

        # Adding unique constraint on 'Sequence', fields ['db', 'hash']
        db.create_unique('hippo_sequence', ['db_id', 'hash'])

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
            ('db_version', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('last_built', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('hippo', ['Feature_Database'])

        # Adding model 'Feature_In_Database'
        db.create_table('hippo_feature_in_database', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feature', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Feature'])),
            ('feature_database', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Feature_Database'])),
            ('show_feature', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('hippo', ['Feature_In_Database'])

        # Adding model 'Feature_DB_Index'
        db.create_table('hippo_feature_db_index', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('db', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Feature_Database'])),
            ('feature_index', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('feature', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Feature'])),
            ('antisense', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_feature', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('hippo', ['Feature_DB_Index'])

        # Adding unique constraint on 'Feature_DB_Index', fields ['db', 'feature_index']
        db.create_unique('hippo_feature_db_index', ['db_id', 'feature_index'])

        # Adding model 'Sequence_Feature_Annotated'
        db.create_table('hippo_sequence_feature_annotated', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sequence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Sequence'])),
            ('start', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('end', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('clockwise', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feature_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('feature_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Feature_Type'])),
            ('orf_frame', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('orf_annotated', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hippo.Sequence_Feature_Annotated'], null=True)),
        ))
        db.send_create_signal('hippo', ['Sequence_Feature_Annotated'])


    def backwards(self, orm):
        # Removing unique constraint on 'Feature_DB_Index', fields ['db', 'feature_index']
        db.delete_unique('hippo_feature_db_index', ['db_id', 'feature_index'])

        # Removing unique constraint on 'Feature', fields ['name', 'hash']
        db.delete_unique('hippo_feature', ['name', 'hash'])

        # Removing unique constraint on 'Sequence', fields ['db', 'hash']
        db.delete_unique('hippo_sequence', ['db_id', 'hash'])

        # Deleting model 'Sequence_Feature'
        db.delete_table('hippo_sequence_feature')

        # Deleting model 'Sequence'
        db.delete_table('hippo_sequence')

        # Deleting model 'Feature_Type'
        db.delete_table('hippo_feature_type')

        # Deleting model 'Feature'
        db.delete_table('hippo_feature')

        # Deleting model 'Feature_Database'
        db.delete_table('hippo_feature_database')

        # Deleting model 'Feature_In_Database'
        db.delete_table('hippo_feature_in_database')

        # Deleting model 'Feature_DB_Index'
        db.delete_table('hippo_feature_db_index')

        # Deleting model 'Sequence_Feature_Annotated'
        db.delete_table('hippo_sequence_feature_annotated')


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
            'db_version': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'features': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hippo.Feature']", 'through': "orm['hippo.Feature_In_Database']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_built': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'hippo.feature_db_index': {
            'Meta': {'unique_together': "(('db', 'feature_index'),)", 'object_name': 'Feature_DB_Index'},
            'antisense': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'db': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature_Database']"}),
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature']"}),
            'feature_index': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show_feature': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'hippo.feature_in_database': {
            'Meta': {'object_name': 'Feature_In_Database'},
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature']"}),
            'feature_database': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature_Database']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show_feature': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'hippo.feature_type': {
            'Meta': {'object_name': 'Feature_Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'hippo.sequence': {
            'Meta': {'unique_together': "(('db', 'hash'),)", 'object_name': 'Sequence'},
            'db': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature_Database']"}),
            'db_version': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sequence': ('django.db.models.fields.TextField', [], {})
        },
        'hippo.sequence_feature': {
            'Meta': {'ordering': "['start', 'end']", 'object_name': 'Sequence_Feature'},
            'clockwise': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'feature_db_index': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature_DB_Index']"}),
            'has_gaps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_variant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sequence': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Sequence']"}),
            'start': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'subset_end': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'subset_start': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'hippo.sequence_feature_annotated': {
            'Meta': {'object_name': 'Sequence_Feature_Annotated'},
            'clockwise': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'feature_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'feature_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Feature_Type']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orf_annotated': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Sequence_Feature_Annotated']", 'null': 'True'}),
            'orf_frame': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'sequence': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hippo.Sequence']"}),
            'start': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['hippo']