# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Game.current_question'
        db.add_column(u'quizz_game', 'current_question',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['quizz.Question']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Game.current_question'
        db.delete_column(u'quizz_game', 'current_question_id')


    models = {
        u'quizz.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'quizz.game': {
            'Meta': {'object_name': 'Game'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'games'", 'symmetrical': 'False', 'to': u"orm['quizz.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_player': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['quizz.Player']"}),
            'current_question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['quizz.Question']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_players': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '4'}),
            'nb_players': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['quizz.Player']"}),
            'secret_id': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'})
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