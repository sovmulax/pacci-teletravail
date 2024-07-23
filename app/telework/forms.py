from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Column, Submit, Div
from .models import DemandeTeleTravail, MotifRefus
from django.forms import DateTimeInput


class DemandeTeleTravailForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DemandeTeleTravailForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Column(
                Div("motif", css_class="mb-3"),
                Div("autre_motif", css_class="mb-3"),
                Div("date_debut", css_class="mb-3"),
                Div("date_fin", css_class="mb-3"),
                Div("lieu", css_class="mb-3"),
                Div("autre_champ_si_nécessaire", css_class="mb-3"),
                Div("commentaire", css_class="mb-3"),
                Div(
                    Submit("submit", "Enregistrer", css_class="btn btn-primary mt-3"),
                    css_class="text-center",
                ),
            ),
        )

    MOTIFS_CHOICES = [
        ("Nécessité professionnelle", "Nécessité professionnelle"),
        (
            "Conditions environnementales défavorables",
            "Conditions environnementales défavorables",
        ),
        (
            "Perturbations sociales et de transport",
            "Perturbations sociales et de transport",
        ),
        ("Cas de force majeure", "Cas de force majeure"),
        (
            "Demandes personnelles exceptionnelles",
            "Demandes personnelles exceptionnelles",
        ),
        ("Autres", "Autres"),
    ]

    def __init__(self, *args, **kwargs):
        super(DemandeTeleTravailForm, self).__init__(*args, **kwargs)
        self.fields["motif"] = forms.ChoiceField(
            choices=self.MOTIFS_CHOICES,
            label="Motif",
            widget=forms.Select(attrs={"class": "form-select"}),
        )

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Column(
                Div("motif", css_class="mb-3"),
                Div("autre_motif", css_class="mb-3"),
                Div("date_debut", css_class="mb-3"),
                Div("date_fin", css_class="mb-3"),
                Div("lieu", css_class="mb-3"),
                Div("autre_champ_si_nécessaire", css_class="mb-3"),
                Div("commentaire", css_class="mb-3"),
                Div(
                    Submit("submit", "Enregistrer", css_class="btn btn-primary mt-3"),
                    css_class="text-center",
                ),
            ),
        )

    autre_motif = forms.CharField(
        label="Spécifiez le motif",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    LIEU_CHOICES = [
        ("Domicile", "A domicile"),
        ("Autre", "Autres"),
    ]
    lieu = forms.ChoiceField(
        choices=LIEU_CHOICES,
        label="Lieu",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    autre_champ_si_nécessaire = forms.CharField(
        label="Préciser le lieu",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = DemandeTeleTravail
        fields = [
            "motif",
            "autre_motif",
            "date_debut",
            "date_fin",
            "lieu",
            "autre_champ_si_nécessaire",
            "commentaire",
        ]
        widgets = {
            "date_debut": DateTimeInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_fin": DateTimeInput(attrs={"type": "date", "class": "form-control"}),
            "commentaire": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        motif = cleaned_data.get("motif")
        autre_motif = cleaned_data.get("autre_motif")
        lieu = cleaned_data.get("lieu")
        autre_champ_si_nécessaire = cleaned_data.get("autre_champ_si_nécessaire")

        if motif == "Autres" and not autre_motif:
            raise forms.ValidationError(
                "Veuillez spécifier le motif dans le champ 'Autres'."
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.motif == "Autres" and instance.autre_motif:
            instance.motif = instance.autre_motif
        if instance.lieu == "Autre" and instance.autre_champ_si_nécessaire:
            instance.lieu = instance.autre_champ_si_nécessaire
        if commit:
            instance.save()
        return instance


class MotifRefusForm(forms.ModelForm):
    class Meta:
        model = MotifRefus
        fields = ["demande", "motif"]
        widgets = {"demande": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        current_demande = kwargs.pop("current_demande", None)
        super().__init__(*args, **kwargs)
        self.fields["demande"].queryset = DemandeTeleTravail.objects.filter(
            statut="en attente"
        )
        if current_demande:
            self.fields["demande"].initial = current_demande

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            "demande",
            "motif",
            Submit("submit", "Valider", css_class="btn btn-primary mt-3"),
        )
