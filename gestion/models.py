from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('tecnico', 'Técnico') # Cambiado de 'agente' a 'tecnico'
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"

# Técnico (Entidad principal)
class Tecnico(models.Model):
    cedula = models.CharField(max_length=10)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=10)
    cargo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='tecnicos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


# Curso
class Curso(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    horas = models.IntegerField()
    instructor = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='cursos/', null=True, blank=True)

    def __str__(self):
        return self.nombre


# Participación (relación entre Técnico y Curso)
class Participacion(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateField()
    estado = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.tecnico} - {self.curso}"
    

# AUTOMATIZACIÓN DE PERFILES
# --------------------------
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # Se crea automáticamente con rol 'tecnico'
        Perfil.objects.create(usuario=instance, rol='tecnico')

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    # Esto asegura que el perfil se guarde cuando el usuario se actualiza
    instance.perfil.save()


class Participacion(models.Model):
    tecnico = models.ForeignKey(Tecnico, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    calificacion = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.tecnico.nombres} - {self.curso.nombre}"