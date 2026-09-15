from django import forms
from .models import Socio, EstadoAptoFisico, Responsable

class SocioForm(forms.ModelForm):

    fecha_nacimiento = forms.DateField(
        required=False,
        input_formats=["%d/%m/%Y"],
        error_messages={
            "invalid": "Ingresá una fecha válida en formato DD/MM/AAAA.",
        },
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "placeholder": "DD/MM/AAAA",
                "inputmode": "numeric",
                "maxlength": "10",
                "autocomplete": "off",
            }
        )
    )

    fecha_presentacion_apto = forms.DateField(
        required=False,
        input_formats=["%d/%m/%Y"],
        error_messages={
            "invalid": "Ingresá una fecha válida en formato DD/MM/AAAA.",
        },
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "placeholder": "DD/MM/AAAA",
                "inputmode": "numeric",
                "maxlength": "10",
                "autocomplete": "off",
            }
        )
    )

    fecha_ingreso = forms.DateField(
        required=True,
        input_formats=["%d/%m/%Y"],
        error_messages={
            "invalid": "Ingresá una fecha válida en formato DD/MM/AAAA.",
        },
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "placeholder": "DD/MM/AAAA",
                "inputmode": "numeric",
                "maxlength": "10",
                "autocomplete": "off",
            }
        )
        
    )

    class Meta:
        model = Socio

        fields = [
            "nombre",
            "apellido",
            "dni",
            "fecha_nacimiento",
            "email",
            "telefono",
            "domicilio",
            "nombre_contacto_emergencia",
            "telefono_emergencia",
            "relacion_contacto_emergencia",
            "apto_fisico",
            "estado_apto_fisico",
            "fecha_presentacion_apto",
            "fecha_ingreso",
        ]

        error_messages = {
            "dni": {
                "unique": "Ya existe un socio registrado con este DNI.",
            }
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "autocomplete": "given-name",
                }
            ),

            "apellido": forms.TextInput(
                attrs={
                    "autocomplete": "family-name",
                }
            ),

            "dni": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "autocomplete": "email",
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "class": "telefono-mask",
                    "inputmode": "numeric",
                    "maxlength": "12",
                }
            ),

            "domicilio": forms.TextInput(
                attrs={
                    "placeholder": "Calle, número, localidad",
                    "autocomplete": "street-address",
                }
            ),

            "telefono_emergencia": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "class": "telefono-mask",
                    "inputmode": "numeric",
                    "maxlength": "12",
                }
            ),
            
            "relacion_contacto_emergencia": forms.TextInput(
                attrs={
                    "placeholder": "Ej. Madre, padre, pareja, amigo/a",
                }
            ),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")

        if not telefono:
            return ""

        numeros = "".join(c for c in telefono if c.isdigit())

        if len(numeros) == 10:
            return f"{numeros[:2]} {numeros[2:6]}-{numeros[6:]}"

        return telefono


    def clean_telefono_emergencia(self):
        telefono = self.cleaned_data.get("telefono_emergencia", "")

        if not telefono:
            return ""

        numeros = "".join(c for c in telefono if c.isdigit())

        if len(numeros) == 10:
            return f"{numeros[:2]} {numeros[2:6]}-{numeros[6:]}"

        return telefono

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["estado_apto_fisico"].empty_label = None

        if not self.instance.pk:
            estado_pendiente = EstadoAptoFisico.objects.filter(
                nombre__iexact="Pendiente"
            ).first()

            if estado_pendiente:
                self.fields["estado_apto_fisico"].initial = estado_pendiente

class ResponsableForm(forms.ModelForm):
    parentesco = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Ej. Madre, padre, tutor"}),
    )

    class Meta:
        model = Responsable

        fields = [
            "nombre",
            "apellido",
            "dni",
            "telefono",
            "email",
            "domicilio",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "autocomplete": "given-name",
                }
            ),

            "apellido": forms.TextInput(
                attrs={
                    "autocomplete": "family-name",
                }
            ),

            "dni": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "autocomplete": "tel",
                    "class": "telefono-mask",
                    "inputmode": "numeric",
                    "maxlength": "12",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "autocomplete": "email",
                }
            ),

            "domicilio": forms.TextInput(
                attrs={
                    "placeholder": "Calle, número, localidad",
                    "autocomplete": "street-address",
                }
            ),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")
        if not telefono:
            return ""

        numeros = "".join(c for c in telefono if c.isdigit())
        if len(numeros) == 10:
            return f"{numeros[:2]} {numeros[2:6]}-{numeros[6:]}"

        return telefono