# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'quizz_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'quizz', ['Category'])

        # Adding model 'Question'
        db.create_table(u'quizz_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('answer_1', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('answer_2', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('answer_3', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('answer_4', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('difficulty', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quizz.Category'])),
        ))
        db.send_create_signal(u'quizz', ['Question'])

        # Adding model 'Game'
        db.create_table(u'quizz_game', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('secret_id', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
        ))
        db.send_create_signal(u'quizz', ['Game'])

        # Adding model 'Player'
        db.create_table(u'quizz_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='players', null=True, to=orm['quizz.Game'])),
        ))
        db.send_create_signal(u'quizz', ['Player'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'quizz_category')

        # Deleting model 'Question'
        db.delete_table(u'quizz_question')

        # Deleting model 'Game'
        db.delete_table(u'quizz_game')

        # Deleting model 'Player'
        db.delete_table(u'quizz_player')


    models = {
        u'quizz.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'quizz.game': {
            'Meta': {'object_name': 'Game'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'secret_id': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'})
        },
        u'quizz.player': {
            'Meta': {'object_name': 'Player'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'players'", 'null': 'True', 'to': u"orm['quizz.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'quizz.question': {
            'Meta': {'object_name': 'Question'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'answer_1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'answer_2': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'answer_3': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'answer_4': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quizz.Category']"}),
            'difficulty': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['quizz']