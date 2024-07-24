from datetime import datetime

from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from telework.models import DemandeTeleTravail, LiaisonAgentSuperieur, Personnel
from telework.forms import DemandeTeleTravailForm, MotifRefusForm
from braces.views import FormMessagesMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime

from telework.views import MotifRefus


@method_decorator(login_required, name="dispatch")
class DemandeTeleTravailListView_history_admin(ListView):
    model = DemandeTeleTravail
    context_object_name = "DemandeTeleTravail_list_history_admin"
    template_name = (
        "pages/DemandeTeleTravail/DemandeTeleTravail_list_historique_admin.html"
    )

    def get_queryset(self):
        # Obtenez l'utilisateur connecté
        # user = self.request.user

        # Filtrer les instances de Personnel où l'utilisateur est associé
        personnel = self.request.user

        # Si le personnel est trouvé, obtenir le service associé
        if personnel:
            service = personnel.service

            # Filtrer les instances de DemandeTeleTravail en fonction du service et du statut 'accepte' ou 'refuse'
            queryset = DemandeTeleTravail.objects.filter(
                agent__service=service, statut__in=["Accepté", "Refusé"]
            ).order_by("-date_demande")

            # Filtrer par nom si un nom est fourni dans les paramètres de requête
            nom = self.request.GET.get("nom")
            if nom:
                queryset = queryset.filter(agent__username__icontains=nom)

            # Filtrer par une plage de dates si des dates sont fournies dans les paramètres de requête
            date_debut = self.request.GET.get("date_debut")
            date_fin = self.request.GET.get("date_fin")
            if date_debut and date_fin:
                try:
                    debut = timezone.datetime.strptime(date_debut, "%Y-%m-%d").date()
                    fin = timezone.datetime.strptime(date_fin, "%Y-%m-%d").date()
                    # Filtrer les demandes qui ont une date_demande comprise entre debut et fin
                    queryset = queryset.filter(date_demande__date__range=[debut, fin])
                except ValueError:
                    pass  # Gérer les erreurs de format de date

        else:
            # Si le personnel n'est pas trouvé, renvoyer une queryset vide
            queryset = DemandeTeleTravail.objects.none()

        return queryset


@method_decorator(login_required, name="dispatch")
class DemandeTeleTravailListView_history(ListView):
    model = DemandeTeleTravail
    context_object_name = "DemandeTeleTravail_list_history"
    template_name = "pages/DemandeTeleTravail/DemandeTeleTravail_list_historique.html"

    def get_queryset(self):
        # Filtrer les demandes liées à l'utilisateur connecté
        user = self.request.user
        queryset = DemandeTeleTravail.objects.filter(
            agent=user, statut__in=["Accepté", "Refusé"]
        ).order_by("-date_demande")

        # Récupérer les dates de début et de fin depuis les paramètres de requête
        date_debut = self.request.GET.get("date_debut")
        date_fin = self.request.GET.get("date_fin")

        # Validez et convertissez les dates de début et de fin en objets datetime
        if date_debut and date_fin:
            try:
                debut = datetime.strptime(date_debut, "%Y-%m-%d").date()
                fin = datetime.strptime(date_fin, "%Y-%m-%d").date()
            except ValueError:
                # Gérez le format de date invalide ou d'autres erreurs
                # Vous pouvez fournir des dates par défaut ou rediriger vers une page d'erreur
                pass

            # Filtrez les demandes de télétravail en fonction de la plage de dates spécifiée
            if debut and fin:
                queryset = queryset.filter(date_demande__date__range=[debut, fin])

        return queryset


@method_decorator(login_required, name="dispatch")
class DemandeTeleTravailListView_Attente(ListView):
    model = DemandeTeleTravail
    context_object_name = "DemandeTeleTravail_list_attente"
    template_name = "pages/DemandeTeleTravail/DemandeTeleTravail_list_attente.html"

    def get_queryset(self):
        # Filtrer les demandes liées à l'utilisateur connecté et son service lié
        user = self.request.user
        queryset = DemandeTeleTravail.objects.filter(
            agent=user, statut="en attente"
        ).order_by("-date_demande")
        return queryset


@method_decorator(login_required, name="dispatch")
class DemandeTeleTravailListView_Attente_admin(ListView):
    model = DemandeTeleTravail
    context_object_name = "DemandeTeleTravail_list_attente_admin"
    template_name = (
        "pages/DemandeTeleTravail/DemandeTeleTravail_list_attente_admin.html"
    )

    def get_queryset(self):
        # Obtenez l'utilisateur connecté
        user = self.request.user

        # Filtrer les instances de Personnel où l'utilisateur est associé
        personnel = self.request.user

        # Si le personnel est trouvé, obtenir le service associé
        if personnel:
            service = personnel.service

            # Filtrer les instances de DemandeTeleTravail en fonction du service et du statut 'en_attente'
            queryset = DemandeTeleTravail.objects.filter(
                agent__service=service, statut="en attente"
            ).order_by("-date_demande")
        else:
            # Si le personnel n'est pas trouvé, renvoyer une queryset vide
            queryset = DemandeTeleTravail.objects.none()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter le nombre d'éléments à votre contexte
        context["demande_count"] = self.get_queryset().count()
        return context


def accepter_demande(request, demandeTeleTravail_id):
    demande = get_object_or_404(DemandeTeleTravail, id=demandeTeleTravail_id)

    # Vérifiez les autorisations pour accepter la demande ici, si nécessaire

    superieur = request.user

    # Acceptez la demande en utilisant la méthode de votre modèle
    demande.accepter_demande(superieur)

    # Envoyez un e-mail à l'utilisateur pour lui notifier l'acceptation de la demande
    subject_user = "Demande de télétravail acceptée"
    message_user = "Votre demande de télétravail a été acceptée."
    send_mail(subject_user, message_user, "intranet@pac-ci.org", [demande.agent.email])

    # Envoyez un e-mail au supérieur hiérarchique pour le notifier
    subject_superieur = "Demande de télétravail acceptée"
    message_superieur = f"La demande de télétravail de {demande.agent} a été acceptée."
    send_mail(
        subject_superieur, message_superieur, "intranet@pac-ci.org", [superieur.email]
    )

    # # Envoyez un e-mail à une autre adresse spécifique, si nécessaire
    # autre_email = 'exemple@example.com'
    # subject_autre = f"Réception de la demande de télétravail au niveau du service {request.user.service}"
    # message_autre = f'La demande de télétravail de {demande.agent} a été acceptée.'
    # send_mail(subject_autre, message_autre, 'kouassijunior614@gmail.com', [autre_email])

    # Ajoutez un message de réussite pour informer l'utilisateur de l'acceptation de la demande
    messages.add_message(
        request, messages.SUCCESS, "La demande a été acceptée avec succès."
    )

    return redirect("DemandeTeleTravail_list_attente_admin")


@login_required
def refuser_demande(request, demandeTeleTravail_id):
    demande = get_object_or_404(DemandeTeleTravail, id=demandeTeleTravail_id)
    superieur = request.user

    if request.method == "POST":
        form = MotifRefusForm(request.POST, current_demande=demande)
        if form.is_valid():
            motif_refus = form.save(commit=False)
            motif_refus.demande = demande
            motif_refus.save()

            demande.statut = "Refusé"
            demande.save()

            subject_user = "Demande de télétravail refusée"
            message_user = f"Votre demande de télétravail a été refusée."
            send_mail(
                subject_user, message_user, "intranet@pac-ci.org", [demande.agent.email]
            )

            subject_superieur = "Demande de télétravail refusée"
            message_superieur = (
                f"La demande de télétravail de {demande.agent} a été refusée."
            )
            send_mail(
                subject_superieur,
                message_superieur,
                "intranet@pac-ci.org",
                [superieur.email],
            )

            return redirect("DemandeTeleTravail_list_attente_admin")
    else:
        form = MotifRefusForm(current_demande=demande)

    context = {
        "form": form,
        "demande": demande,
    }
    return render(request, "pages/motif_refus/MotifRefus_create.html", context)


@method_decorator(login_required, name="dispatch")
class DemandeTeleTravailCreateview(CreateView):
    model = DemandeTeleTravail
    form_class = DemandeTeleTravailForm
    template_name = "pages/DemandeTeleTravail/DemandeTeleTravail_create.html"
    success_url = reverse_lazy("DemandeTeleTravail_list_attente")
    form_invalid_message = "Oups, quelque chose s'est mal passé!"

    def get_form_valid_message(self):
        return "{0} Transaction ajoutée avec succès!".format(self.object.name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["method"] = "post"
        return context

    def form_valid(self, form):
        user = self.request.user
        # personnel = get_object_or_404(Personnel, user=user)
        form.instance.agent = user

        date_debut = form.cleaned_data["date_debut"]
        date_fin = form.cleaned_data["date_fin"]
        time_difference = date_fin - date_debut
        days_difference = time_difference.days + 1

        messages.add_message(
            self.request,
            messages.SUCCESS,
            f" Mme/M {user}  votre demande de {days_difference} jours a été envoyée à votre supérieur.",
        )

        mail = user.email
        liaison_agent = LiaisonAgentSuperieur.objects.filter(agent=user).first()

        if liaison_agent:
            superieur_email = liaison_agent.superieur.email

            # Envoyer un e-mail à l'utilisateur
            subject_user = "Confirmation de la demande de télétravail"
            message_user = "Votre demande de télétravail a été soumise avec succès."
            send_mail(subject_user, message_user, "intranet@pac-ci.org", [str(mail)])

            # from_email = "intranet@pac-ci.org"
            # subject = "Confirmation de la demande de télétravail"
            # message_user = "Votre demande de télétravail a été soumise avec succès."
            # to = ["personnel@pac-ci.org"]
            # message = EmailMultiAlternatives(
            #     subject=subject_user, body=message_user, from_email=from_email, to=to
            # )
            # message.send(fail_silently=False)

            # Envoyer un e-mail au supérieur hiérarchique
            subject_superieur = "Nouvelle demande de télétravail"
            message_superieur = f"Une nouvelle demande de télétravail a été soumise par {user.username}."
            send_mail(
                subject_superieur,
                message_superieur,
                "intranet@pac-ci.org",
                [superieur_email],
            )
        else:
            print("Aucune liaison d'agent supérieur trouvée pour cet utilisateur.")

        return super().form_valid(form)

    def form_invalid(self, form):
        user = self.request.user
        date_debut = form.cleaned_data["date_debut"]
        date_fin = form.cleaned_data["date_fin"]

        aujourdhui = timezone.now().date()
        if date_debut <= aujourdhui:
            messages.error(
                self.request,
                f" Mme/M {user}, veuillez vérifier votre date de demande de debut de télétravail",
            )

        time_difference = date_fin - date_debut
        days_difference = time_difference.days + 1

        if days_difference > 2:
            messages.error(
                self.request,
                f" Mme/M {user}, votre demande de télétravail ne doit pas excéder un ou deux jours.",
            )
        if days_difference <= 0:
            messages.error(
                self.request,
                f" Mme/M {user}, votre demande de télétravail ne doit pas excéder un ou deux jours.",
            )

        return super().form_invalid(form)


@method_decorator(login_required, name="dispatch")
class DemandeTeleTravailUpdateView(UpdateView):
    model = DemandeTeleTravail
    form_class = DemandeTeleTravailForm
    template_name = "pages/DemandeTeleTravail/DemandeTeleTravail_create.html"
    success_url = reverse_lazy("DemandeTeleTravail_list_history")
    form_invalid_message = "Oups, quelque chose s'est mal passé!"

    def get_form_valid_message(self):
        return " Modification effectuée avec succès!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["method"] = "put"
        return context

    def form_valid(self, form):
        user = self.request.user
        personnel = get_object_or_404(Personnel, user=user)
        form.instance.agent = user

        date_debut = form.cleaned_data["date_debut"]
        date_fin = form.cleaned_data["date_fin"]
        time_difference = date_fin - date_debut
        days_difference = time_difference.days + 1

        messages.add_message(
            self.request,
            messages.SUCCESS,
            f" Mme/M {user}  votre demande de {days_difference} jours a été modifiée.",
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        user = self.request.user
        date_debut = form.cleaned_data["date_debut"]
        date_fin = form.cleaned_data["date_fin"]

        aujourdhui = timezone.now().date()
        if date_debut <= aujourdhui:
            messages.error(
                self.request,
                f" Mme/M {user} , Veuillez vérifier votre date de demande de debut de télétravail ",
            )

        time_difference = date_fin - date_debut
        days_difference = time_difference.days + 1

        if days_difference > 2:
            messages.error(
                self.request,
                f" Mme/M {user}  votre demande de télétravail doit excéder 1 ou 2 jours",
            )
        if days_difference <= 0:
            messages.error(
                self.request,
                f" Mme/M {user}  votre demande de télétravail doit excéder 1 ou 2 jours",
            )

        return super().form_invalid(form)


def afficher_details_DemandeTeleTravail(request, demandeTeleTravail_id):
    demandeTeleTravail = get_object_or_404(DemandeTeleTravail, id=demandeTeleTravail_id)
    return render(
        request,
        "pages/DemandeTeleTravail/demande_detail.html",
        {"demandeTeleTravail": demandeTeleTravail},
    )


##### PROFILE USER #########


@login_required
def user_profile(request):

    user_personnel = request.user

    try:
        liaison = LiaisonAgentSuperieur.objects.get(agent=user_personnel)
        superior = liaison.superieur
    except LiaisonAgentSuperieur.DoesNotExist:
        superior = None

    total_requests = DemandeTeleTravail.objects.filter(agent=user_personnel).count()
    accepted_requests = DemandeTeleTravail.objects.filter(
        agent=user_personnel, statut="Accepté"
    ).count()
    refused_requests = DemandeTeleTravail.objects.filter(
        agent=user_personnel, statut="Refusé"
    ).count()

    # Access the profile through the OneToOneField relationship

    context = {
        "user_personnel": user_personnel,
        "superior": superior,
        "total_requests": total_requests,
        "accepted_requests": accepted_requests,
        "refused_requests": refused_requests,
    }
    return render(request, "pages/DemandeTeleTravail/user_profil.html", context)
