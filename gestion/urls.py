from django.urls import path
from . import views

urlpatterns = [
    # 1. La raíz ahora es el LOGIN
    path('', views.login_view, name='login'),

    # 2. Rutas del sistema (protegidas)
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.logout_view, name='logout'),

    # Técnicos
    path('tecnicos/', views.listadoTecnicos, name='listadoTecnicos'),
    path('nuevoTecnico/', views.nuevoTecnico, name='nuevoTecnico'),
    path('guardarTecnico/', views.guardarTecnico, name='guardarTecnico'),
    path('editarTecnico/<int:id>/', views.editarTecnico, name='editarTecnico'),
    path('actualizarTecnico/<int:id>/', views.actualizarTecnico, name='actualizarTecnico'),
    path('eliminarTecnico/<int:id>/', views.eliminarTecnico, name='eliminarTecnico'),

    # Cursos
    path('cursos/', views.listadoCursos, name='listadoCursos'),
    path('nuevoCurso/', views.nuevoCurso, name='nuevoCurso'),
    path('guardarCurso/', views.guardarCurso, name='guardarCurso'),
    path('editarCurso/<int:id>/', views.editarCurso, name='editarCurso'),
    path('actualizarCurso/<int:id>/', views.actualizarCurso, name='actualizarCurso'),
    path('eliminarCurso/<int:id>/', views.eliminarCurso, name='eliminarCurso'),

    # Participaciones
    path('participaciones/', views.listadoParticipaciones, name='listadoParticipaciones'),
    # Asegúrate de que esta línea esté presente y se vea así:
    path('nuevaParticipacion/', views.nuevaParticipacion, name='nuevopar'),

    # Añade esto a tus urlpatterns en gestion/urls.py
    path('certificados-listado/', views.lista_certificados, name='listadoCertificados'),
    path('certificado/<int:id>/', views.generar_certificado, name='listadocer'),
    path('validar/<int:id>/', views.validar_certificado, name='validar_certificado'),
    path('eliminarParticipacion/<int:id>/', views.eliminarParticipacion, name='eliminarParticipacion'),

    
]