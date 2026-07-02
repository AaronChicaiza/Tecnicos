from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Tecnico, Curso, Participacion, Perfil
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import qrcode
from io import BytesIO
from PIL import Image
from reportlab.lib.utils import ImageReader
from django.core.exceptions import PermissionDenied
import os
from django.shortcuts import redirect
from .models import Tecnico
from django.shortcuts import render, get_object_or_404

@login_required
def inicio(request):
    perfil = Perfil.objects.get(usuario=request.user)
    return render(request, "inicio.html", {"perfil": perfil}) 

@login_required
def listadoTecnicos(request):
    perfil = Perfil.objects.get(usuario=request.user) # <--- OBTÉN EL PERFIL
    
    if perfil.rol == 'admin':
        tecnicos = Tecnico.objects.all()
    else:
        tecnicos = Tecnico.objects.filter(correo=request.user.email)
    
    # <--- PASA EL PERFIL AL RENDER
    return render(request, "tecnicos/listadotec.html", {"tecnicos": tecnicos, "perfil": perfil})

@login_required
def nuevoTecnico(request):
    perfil = Perfil.objects.get(usuario=request.user) # Obtén el perfil
    return render(request, "tecnicos/nuevotec.html", {"perfil": perfil}) # Pásalo

def guardarTecnico(request):
    # Captura de datos básicos
    cedula = request.POST["cedula"]
    nombres = request.POST["nombres"]
    apellidos = request.POST["apellidos"]
    correo = request.POST["correo"]
    telefono = request.POST["telefono"]
    cargo = request.POST["cargo"]
    
    # Captura de la imagen desde el formulario
    foto = request.FILES.get("foto")

    # Creación del objeto incluyendo la foto
    Tecnico.objects.create(
        cedula=cedula,
        nombres=nombres,
        apellidos=apellidos,
        correo=correo,
        telefono=telefono,
        cargo=cargo,
        foto=foto
    )

    messages.success(request, "Técnico registrado correctamente")

    return redirect('listadoTecnicos')

def editarTecnico(request, id):

    tecnico = Tecnico.objects.get(id=id)

    return render(request,
                  "tecnicos/editartec.html",
                  {
                      "tecnico": tecnico
                  })

def actualizarTecnico(request, id):
    # Obtenemos el objeto actual
    tecnico = Tecnico.objects.get(id=id)

    # Actualizamos los campos de texto
    tecnico.cedula = request.POST["cedula"]
    tecnico.nombres = request.POST["nombres"]
    tecnico.apellidos = request.POST["apellidos"]
    tecnico.correo = request.POST["correo"]
    tecnico.telefono = request.POST["telefono"]
    tecnico.cargo = request.POST["cargo"]

    # Gestión de la imagen
    if request.FILES.get("foto"):
        # 1. Si ya existe una foto anterior, la eliminamos físicamente del disco
        if tecnico.foto and os.path.isfile(tecnico.foto.path):
            os.remove(tecnico.foto.path)
        
        # 2. Asignamos la nueva imagen
        tecnico.foto = request.FILES.get("foto")

    # Guardamos los cambios en la base de datos
    tecnico.save()

    messages.success(request, "Técnico actualizado correctamente")

    return redirect('listadoTecnicos')

def eliminarTecnico(request, id):
    # 1. Obtenemos el objeto
    tecnico = Tecnico.objects.get(id=id)

    # 2. Si tiene una foto, la eliminamos físicamente del servidor
    if tecnico.foto and os.path.isfile(tecnico.foto.path):
        os.remove(tecnico.foto.path)

    # 3. Eliminamos el registro de la base de datos
    tecnico.delete()

    messages.success(request, "Técnico eliminado correctamente")

    return redirect('listadoTecnicos')

def listadoCursos(request):
    # SIEMPRE obtén el perfil antes de renderizar
    perfil = Perfil.objects.get(usuario=request.user)
    cursos = Curso.objects.all()
    # Y pásalo al render
    return render(request, "cursos/listadocursos.html", {"cursos": cursos, "perfil": perfil})

@login_required
def nuevoCurso(request):
    perfil = Perfil.objects.get(usuario=request.user) # Obtén el perfil
    return render(request, "cursos/nuevocurso.html", {"perfil": perfil}) # Pásalo

def guardarCurso(request):
    if request.method == 'POST':
        # Capturamos los datos
        nombre = request.POST["nombre"]
        descripcion = request.POST["descripcion"]
        fecha_inicio = request.POST["fecha_inicio"]
        fecha_fin = request.POST["fecha_fin"]
        horas = request.POST["horas"]
        instructor = request.POST["instructor"]
        
        # Capturamos la imagen (debe coincidir con el 'name' en tu input del HTML)
        imagen = request.FILES.get("imagen")

        # Creamos el objeto incluyendo la imagen
        Curso.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            horas=horas,
            instructor=instructor,
            imagen=imagen  # Guardamos la referencia del archivo
        )
        
        messages.success(request, "Curso registrado correctamente")
        return redirect('listadoCursos')
    
    return redirect('nuevoCurso')

# --- Funciones de Edición y Eliminación para Cursos ---

def editarCurso(request, id):
    # Buscamos el curso específico en la base de datos
    curso = Curso.objects.get(id=id)
    return render(request, "cursos/editarcursos.html", {"curso": curso})

def actualizarCurso(request, id):
    if request.method == 'POST':
        # Buscamos el curso
        curso = Curso.objects.get(id=id)
        
        # 1. Actualizamos los campos de texto
        curso.nombre = request.POST["nombre"]
        curso.descripcion = request.POST["descripcion"]
        curso.fecha_inicio = request.POST["fecha_inicio"]
        curso.fecha_fin = request.POST["fecha_fin"]
        curso.horas = request.POST["horas"]
        curso.instructor = request.POST["instructor"]
        
        # 2. Gestión de la imagen
        # Verificamos si el usuario envió un archivo en el campo "imagen"
        if request.FILES.get("imagen"):
            # Si ya existía una imagen previa, la borramos del disco para no ocupar espacio
            if curso.imagen and os.path.isfile(curso.imagen.path):
                os.remove(curso.imagen.path)
            
            # Asignamos la nueva imagen al modelo
            curso.imagen = request.FILES.get("imagen")
        
        # 3. Guardamos los cambios
        curso.save()
        
        messages.success(request, "Curso actualizado correctamente")
        return redirect('listadoCursos')
    
    return redirect('listadoCursos')

def eliminarCurso(request, id):
    # 1. Buscamos el curso
    curso = Curso.objects.get(id=id)

    # 2. Borramos la imagen del disco si existe
    if curso.imagen and os.path.isfile(curso.imagen.path):
        os.remove(curso.imagen.path)

    # 3. Borramos el registro de la base de datos
    curso.delete()
    
    messages.success(request, "Curso eliminado correctamente")
    return redirect('listadoCursos')

# LOGIN
# -------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            perfil = Perfil.objects.filter(usuario=user).first()
            if not perfil:
                # AQUÍ ESTABA EL ERROR: Cambiado a 'usuarios/login.html'
                return render(request, "usuarios/login.html", {
                    "error": "Usuario sin rol asignado"
                })
            return redirect("inicio")

        # AQUÍ TAMBIÉN: Cambiado a 'usuarios/login.html'
        return render(request, "usuarios/login.html", {
            "error": "Usuario o contraseña incorrectos"
        })

    # Y AQUÍ TAMBIÉN: Cambiado a 'usuarios/login.html'
    return render(request, "usuarios/login.html")

# -------------------------
# LOGOUT
# -------------------------
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def listadoParticipaciones(request):
    perfil = Perfil.objects.get(usuario=request.user)
    
    # Lógica de seguridad:
    if perfil.rol == 'admin':
        # El administrador ve todo el listado global
        participaciones = Participacion.objects.all()
    else:
        # El técnico ve SOLAMENTE las participaciones asociadas a su perfil
        # Filtramos buscando el técnico por el email del usuario logueado
        participaciones = Participacion.objects.filter(tecnico__correo=request.user.email)
    
    print(f"DEBUG: Mostrando {participaciones.count()} participaciones para {request.user.email}")
    
    return render(request, "participaciones/listadopar.html", {
        "participaciones": participaciones, 
        "perfil": perfil
    })

@login_required
def nuevaParticipacion(request):
    perfil = Perfil.objects.get(usuario=request.user)
    
    if request.method == 'POST':
        c_id = request.POST.get('curso_id')
        t_id = request.POST.get('tecnico_id')
        
        # DEBUG: ¿Qué valores llegan realmente?
        print(f"DEBUG POST: Curso={c_id}, Tecnico={t_id}")
        
        if not t_id:
            tecnico = Tecnico.objects.get(correo=request.user.email)
            t_id = tecnico.id
        
        # Guardamos y capturamos el resultado
        nueva = Participacion.objects.create(tecnico_id=t_id, curso_id=c_id)
        
        # Verificamos si realmente existe en BD después de crear
        existe = Participacion.objects.filter(id=nueva.id).exists()
        print(f"DEBUG: ¿Registro guardado en BD? {existe}")
        
        return redirect('listadoParticipaciones')
    
    # DATOS PARA EL FORMULARIO (GET)
    cursos = Curso.objects.all()
    tecnicos = Tecnico.objects.all()
    
    tecnico_logueado = None
    if perfil.rol != 'admin':
        try:
            tecnico_logueado = Tecnico.objects.get(correo=request.user.email)
        except Tecnico.DoesNotExist:
            pass # O manejar error si el técnico no existe en la tabla Técnico
    
    return render(request, "participaciones/nuevopar.html", {
        "cursos": cursos,
        "tecnicos": tecnicos,
        "perfil": perfil,
        "tecnico_logueado": tecnico_logueado
    })

@login_required
def lista_certificados(request):
    # 1. Obtenemos el perfil (necesario para el menú base.html)
    perfil = Perfil.objects.get(usuario=request.user)
    
    # 2. Lógica de filtrado
    if perfil.rol == 'admin':
        participaciones = Participacion.objects.all()
    else:
        participaciones = Participacion.objects.filter(tecnico__correo=request.user.email)
    
    # 3. Enviamos AMBOS datos al render
    return render(request, "certificados/listadocer.html", {
        "participaciones": participaciones, 
        "perfil": perfil
    })

def generar_certificado(request, id):
    participacion = get_object_or_404(Participacion, id=id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificado_{participacion.tecnico.nombres}.pdf"'
    
    p = canvas.Canvas(response)
    
    # Diseño del Certificado
    p.setFont("Helvetica-Bold", 30)
    p.drawCentredString(300, 700, "CERTIFICADO DE APROBACIÓN")
    p.setFont("Helvetica", 18)
    p.drawCentredString(300, 650, "Otorgado a:")
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(300, 600, f"{participacion.tecnico.nombres} {participacion.tecnico.apellidos}")
    p.setFont("Helvetica", 18)
    p.drawCentredString(300, 550, f"Por haber completado satisfactoriamente el curso:")
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(300, 500, f"{participacion.curso.nombre}")
    
    # GENERACIÓN DEL QR CON ALTA CALIDAD (Para lectura web)
    domain = request.get_host() 
    url_valida = f"http://{domain}/validar/{participacion.id}/"
    
    qr_config = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10, 
        border=4, 
    )
    qr_config.add_data(url_valida)
    qr_config.make(fit=True)
    
    qr_img_obj = qr_config.make_image(fill_color="black", back_color="white")
    
    qr_img = BytesIO()
    qr_img_obj.save(qr_img, format='PNG')
    qr_img.seek(0)
    
    reader = ImageReader(qr_img)
    p.drawImage(reader, 230, 280, width=140, height=140)
    
    p.showPage()
    p.save()
    return response

def validar_certificado(request, id):
    try:
        participacion = Participacion.objects.get(id=id)
        # HTML limpio y profesional
        mensaje = f"""
        <html>
            <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
            <body style="text-align:center; font-family:sans-serif; padding:20px; background-color: #f4f4f4;">
                <div style="background:white; padding:20px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.1);">
                    <h1 style="color:green;">CURSO COMPLETADO</h1>
                    <p><strong>Estudiante:</strong> {participacion.tecnico.nombres} {participacion.tecnico.apellidos}</p>
                    <p><strong>Curso:</strong> {participacion.curso.nombre}</p>
                    <div style="background:#d4edda; padding:10px; color:#155724; font-weight:bold;">Estado: Aprobado</div>
                </div>
            </body>
        </html>
        """
    except Participacion.DoesNotExist:
        mensaje = "<h1>ERROR</h1><p>Certificado no encontrado.</p>"
        
    return HttpResponse(mensaje)

@login_required
def eliminarParticipacion(request, id):
    # Verificamos si el perfil del usuario actual es 'admin'
    if request.user.perfil.rol != 'admin':
        raise PermissionDenied  # Esto lanza un error 403 Forbidden
        
    participacion = Participacion.objects.get(id=id)
    participacion.delete()
    messages.success(request, "Certificado eliminado exitosamente.")
    return redirect('listadoCertificados')