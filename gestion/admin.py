from django.contrib import admin
from .models import Tecnico, Curso, Participacion

admin.site.register(Tecnico)
admin.site.register(Curso)
admin.site.register(Participacion)