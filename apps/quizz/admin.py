from django.contrib import admin
from .models import Category, Question, Game, Player

admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Game)
admin.site.register(Player)
