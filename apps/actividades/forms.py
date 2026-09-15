from django import forms

from apps.usuarios.models import Usuario

from .models import (
    NOMBRES_ESTADOS_PREDEFINIDOS,
    Actividad,
    Asistencia,
    EstadoActividad,
    Horario,
    Inscripcion,
    Profesor
)


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ["nombre", "descripcion", "estado_actividad"]

        widgets = {
            # Antes era un desplegable que leía todos los estados de la
            # tabla (incluyendo cualquiera que el admin hubiera cargado
            # a mano). Ahora son tres botones fijos: Activo, Inactivo,
            # Suspendido.
            "estado_actividad": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estado_actividad"].queryset = EstadoActividad.objects.filter(
            nombre__in=NOMBRES_ESTADOS_PREDEFINIDOS
        )
        self.fields["estado_actividad"].empty_label = None


class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ["actividad", "profesor", "dia", "hora_inicio", "hora_fin", "cupo"]

        widgets = {
            # El campo "dia" del modelo ahora tiene choices (ver
            # apps.actividades.models.DIAS_SEMANA), así que ModelForm ya
            # renderiza un <select> en vez de un input de texto libre.
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get("dia")
        profesor = cleaned_data.get("profesor")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if not dia or not profesor or not hora_inicio or not hora_fin:
            return cleaned_data

        horarios_solapados = Horario.objects.filter(
            dia=dia,
            profesor=profesor,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        ).exclude(pk=self.instance.pk)

        horario_solapado = horarios_solapados.select_related("actividad", "profesor").first()
        if horario_solapado:
            raise forms.ValidationError(
                "El profesor ya tiene un horario que se solapa con la actividad "
                f'"{horario_solapado.actividad.nombre}" '
                f"({horario_solapado.hora_inicio.strftime('%H:%M')} a "
                f"{horario_solapado.hora_fin.strftime('%H:%M')}) "
                f"del día {horario_solapado.dia}."
            )

        return cleaned_data


class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ["socio", "horario", "observacion"]

    def clean(self):
        cleaned_data = super().clean()
        horario = cleaned_data.get("horario")

        if horario is None:
            return cleaned_data

        # El modelo ya evita una inscripción duplicada del mismo socio al
        # mismo horario (UniqueConstraint), pero nada impedía superar el
        # cupo de la clase. Se valida acá porque es una regla de
        # negocio, no una restricción de integridad de la tabla.
        inscriptos = horario.inscripciones.exclude(pk=self.instance.pk)

        if inscriptos.count() >= horario.cupo:
            raise forms.ValidationError(
                f"El horario \"{horario}\" ya alcanzó su cupo máximo "
                f"({horario.cupo}). No se pueden agregar más inscripciones."
            )

        return cleaned_data


class AsistenciaForm(forms.ModelForm):
    """Solo para corregir un registro de asistencia ya tomado (fecha,
    hora o si finalmente estuvo presente/ausente). A propósito NO
    incluye socio/horario/profesor: permitir reasignarlos libremente
    era exactamente el problema que tenía el alta manual anterior
    (asociar a cualquier socio con cualquier horario y profesor, sin
    relación con la inscripción real)."""

    class Meta:
        model = Asistencia
        fields = ["presente", "fecha", "hora"]

        widgets = {
            "presente": forms.RadioSelect(
                choices=[(True, "Presente"), (False, "Ausente")]
            ),
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora": forms.TimeInput(attrs={"type": "time"}),
        }



class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        exclude = ['usuario']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ingrese el nombre'}),
            'apellido': forms.TextInput(attrs={'placeholder': 'Ingrese el apellido'}),
            'dni': forms.TextInput(attrs={'placeholder': 'Número de DNI'}),
            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'style': 'height: 42px; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px 14px; width: 100%;'
                }
            ),

            'fecha_ingreso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'style': 'height: 42px; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px 14px; width: 100%;'
                }
            ),

            'telefono': forms.TextInput(attrs={'placeholder': 'Ej: 1123456789'}),
            'telefono_2': forms.TextInput(attrs={'placeholder': 'Opcional'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'domicilio': forms.TextInput(attrs={'placeholder': 'Calle, número, localidad'}),
            'estado_profesor': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_dni(self):
        dni = self.cleaned_data['dni']

        if not self.instance.pk and Usuario.objects.filter(username=dni).exists():
            raise forms.ValidationError(
                'Ya existe un usuario con este DNI. No se puede crear el profesor.'
            )

        return dni