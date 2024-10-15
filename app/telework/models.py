from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid
from django.contrib.auth.models import AbstractUser


class TypePersonnel(SafeDeleteModel, HistoricalRecords):

    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(
        max_length=50,
        choices=[
            ("agent", "Agent"),
            ("superieur_hierarchique", "Supérieur hiérarchique"),
        ],
    )

    @classmethod
    def get_default_pk(cls):
        service, created = cls.objects.get_or_create(
            nom="agent",
        )
        return service.pk

    def __str__(self):
        return self.nom


class Service(SafeDeleteModel, HistoricalRecords):

    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=50)

    @classmethod
    def get_default_pk(cls):
        service, created = cls.objects.get_or_create(
            nom="Attente",
        )
        return service.pk

    def __str__(self):
        return self.nom


class Personnel(AbstractUser, SafeDeleteModel, HistoricalRecords):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    type_personnel = models.ForeignKey(
        TypePersonnel,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=TypePersonnel.get_default_pk,
    )
    password = models.CharField(max_length=200)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=Service.get_default_pk,
    )
    email = models.EmailField("Email", blank=True, null=True)
    photo = models.ImageField(
        "Photo", upload_to="profile_photos/", blank=True, null=True
    )

    def __str__(self):
        return self.username


class MotifRefus(models.Model):
    demande = models.OneToOneField(
        "DemandeTeleTravail", on_delete=models.CASCADE, related_name="motif_refus"
    )
    motif = models.TextField()

    def clean(self):
        # Vérifier si la demande associée a le statut 'Refusé'
        if self.demande and self.demande.statut != "en attente":
            raise ValidationError(
                "La demande associée doit avoir le statut 'en attente' pour ajouter un motif de refus."
            )

        # Vérifier si le champ 'motif' n'est pas vide
        if not self.motif.strip():
            raise ValidationError("Le motif de refus ne peut pas être vide.")

    @classmethod
    def get_refused_demands(cls):
        # Récupérer les demandes avec le statut 'refuse' mais sans motif de refus associé
        motifs_refuses = MotifRefus.objects.values_list("demande", flat=True)
        return DemandeTeleTravail.objects.filter(statut="Refusé").exclude(
            id__in=motifs_refuses
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Retirer la demande de la liste une fois qu'elle a un motif de refus
        self.demande.save()

    def __str__(self):
        return f" {self.motif}"


class DemandeTeleTravail(SafeDeleteModel, HistoricalRecords):
    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)

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

    LIEU_CHOICES = [
        ("Domicile", "Domicile"),
        ("Autre", "Autre"),
    ]
    agent = models.ForeignKey("Personnel", on_delete=models.CASCADE)
    motif = models.CharField(max_length=50, choices=MOTIFS_CHOICES)
    autre_motif = models.CharField(
        max_length=50, blank=True
    )  # Rendre autre_motif facultatif
    date_debut = models.DateField()
    date_fin = models.DateField()
    lieu = models.CharField(max_length=100, choices=LIEU_CHOICES, default="Domicile")
    autre_champ_si_nécessaire = models.CharField(
        max_length=50, blank=True
    )  # Rendre autre_champ_si_nécessaire facultatif
    commentaire = models.TextField(blank=True)

    date_demande = models.DateTimeField(default=timezone.now, editable=False)
    statut = models.CharField(
        max_length=10,
        default="en attente",
        editable=False,
        choices=[
            ("en attente", "En attente"),
            ("Refusé", "Refusé"),
            ("Accepté", "Accepté"),
        ],
    )
    date_signature_superieur = models.DateTimeField(
        default=timezone.now, editable=False
    )

    def accepter_demande(self, superieur):
        if superieur.type_personnel.nom == "superieur_hierarchique":
            # Permettre seulement au supérieur hiérarchique de changer le statut
            if self.statut == "en attente":
                self.statut = "Accepté"
                self.date_signature_superieur = timezone.now()
                self.save()
        else:
            raise ValidationError(
                "Seuls les supérieurs hiérarchiques peuvent accepter une demande de télétravail."
            )

    def refuser_demande(self, superieur):
        if superieur.type_personnel.nom == "superieur_hierarchique":
            # Permettre seulement au supérieur hiérarchique de changer le statut
            if self.statut == "en attente":
                self.statut = "Refusé"
                self.date_signature_superieur = timezone.now()
                self.save()

        else:
            raise ValidationError(
                "Seuls les supérieurs hiérarchiques peuvent refuser une demande de télétravail."
            )

    @receiver(pre_save, sender="telework.DemandeTeleTravail")
    def supprimer_demandes_expirees(sender, instance, **kwargs):
        if (
            instance.statut == "en attente"
            and instance.date_fin < timezone.now().date()
        ):
            instance.delete()

    def __str__(self):
        return f"{self.agent.username} - {self.statut} - {self.motif}"

    def clean(self):
        print("La méthode clean est appelée.")
        aujourdhui = timezone.now().date()
        if self.date_debut <= aujourdhui:
            raise ValidationError(
                "La date de la demande ne peut être antérieure ou égale à la date du jour."
            )

        if self.date_debut and self.date_fin:
            time_difference = self.date_fin - self.date_debut
            days_difference = time_difference.days + 1

            print("Différence de jours :", days_difference)

            if days_difference > 2:
                raise ValidationError(
                    "La période de télétravail ne peut pas dépasser deux jours."
                )

            if days_difference <= 0:
                raise ValidationError(
                    "La période de télétravail ne peut pas être negatif ."
                )
        if self.motif != "Autres":
            self.autre_motif = (
                ""  # Réinitialise autre_motif si le motif n'est pas "Autres"
            )
            self.autre_champ_si_nécessaire = (
                ""  # Réinitialise autre_champ_si_nécessaire
            )

    def save(self, *args, **kwargs):
        # self.clean()
        # Automatically set date_signature_superieur when the status is changed to accepte or refuse
        if self.statut in ["Accepté", "Refusé"] and not self.date_signature_superieur:
            self.date_signature_superieur = timezone.now()

        super().save(*args, **kwargs)


class LiaisonAgentSuperieur(SafeDeleteModel, HistoricalRecords):

    _safedelete_policy = SOFT_DELETE_CASCADE
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Personnel, related_name="agent", on_delete=models.CASCADE)
    superieur = models.ForeignKey(
        Personnel, related_name="superieur", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.agent.username} -> {self.superieur.username}"
