from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from django.contrib import messages

from telework.models import DemandeTeleTravail, Service  # Assurez-vous d'importer le modèle Service correctement

def index(request):
    # Assurez-vous que l'utilisateur est connecté et que son service est "Ressource humaine"
    if not request.user.is_authenticated or request.user.personnel.service.nom != "Ressource humaine":
        return render(request, 'error.html', {'message': "Seul les ressources humaines ont les autorisations nécessaires pour accéder à cette page."})

    messages.add_message(request, messages.SUCCESS, "Bienvenue %s" % request.user.username)
    aujourd_hui = timezone.now().date()
    debut_du_mois = aujourd_hui.replace(day=1)
    fin_du_mois = (debut_du_mois + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

    # Requête pour obtenir le nombre total de demandes de télétravail par service pour le mois actuel
    demandes_par_service_mois = Service.objects.annotate(
        total_teletravail=Count('personnel__demandeteletravail', filter=Q(personnel__demandeteletravail__date_demande__range=(debut_du_mois, fin_du_mois)))
    )
    data_for_morris = [{'label': service.nom, 'value': service.total_teletravail} for service in demandes_par_service_mois]

    # Nombre de demande télétravail par jour
    date_actuelle = timezone.now().date()

    # Requête pour obtenir le nombre de demandes par service avec une date de début <= date actuelle
    # et une date de fin > date actuelle
    demandes_par_service = Service.objects.annotate(
        nombre_demandes=Count('personnel__demandeteletravail', filter=(
            Q(personnel__demandeteletravail__date_debut__lte=date_actuelle) &
            Q(personnel__demandeteletravail__date_fin__gt=date_actuelle) &
            Q(personnel__demandeteletravail__statut='Accepté')
        ))
    ).filter(nombre_demandes__gt=0)

    # Calculer le pourcentage de demandes de télétravail pour chaque service
    total_demande_teletravail = DemandeTeleTravail.objects.count()
    data = []

    for service in Service.objects.all():
        total_requests_service = DemandeTeleTravail.objects.filter(agent__service=service).count()
        percentage = (total_requests_service / total_demande_teletravail * 100) if total_demande_teletravail > 0 else 0
        data.append({'service': service.nom, 'percentage': round(percentage, 2)})

    return render(request, 'index.html', {
        'data_for_morris': data_for_morris,
        'demandes_par_service': demandes_par_service,
        'date_actuelle': date_actuelle,
        'data': data,
    })
