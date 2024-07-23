from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from telework.views import (
    DemandeTeleTravailListView_Attente,
    DemandeTeleTravailCreateview,
    DemandeTeleTravailListView_history,
    DemandeTeleTravailListView_history_admin,
    MotifRefuslist,
    MotifRefusCreateview,
    DemandeTeleTravailListView_Attente_admin,
    DemandeTeleTravailUpdateView,
    afficher_details_DemandeTeleTravail,
    accepter_demande,
    refuser_demande,
    index,
    reset_password,
    user_profile,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", auth_views.LoginView.as_view(), name="login"),
    path("index/", index, name="index"),
    path("reset/password/", reset_password, name="reset_password"),
    # URLs pour la gestion des demandes de télétravail
    path(
        "DemandeTeleTravail/DemandeTeleTravailListView_Attente/",
        DemandeTeleTravailListView_Attente.as_view(),
        name="DemandeTeleTravail_list_attente",
    ),
    path(
        "DemandeTeleTravail/DemandeTeleTravailListView_history/",
        DemandeTeleTravailListView_history.as_view(),
        name="DemandeTeleTravail_list_history",
    ),
    path(
        "DemandeTeleTravail/DemandeTeleTravail_create/",
        DemandeTeleTravailCreateview.as_view(),
        name="DemandeTeleTravail_create",
    ),
    path(
        "DemandeTeleTravail/DemandeTeleTravail_UpdateView/<uuid:pk>/",
        DemandeTeleTravailUpdateView.as_view(),
        name="DemandeTeleTravail_UpdateView",
    ),
    path(
        "DemandeTeleTravail/DemandeTeleTravail_detail/<uuid:demandeTeleTravail_id>/",
        afficher_details_DemandeTeleTravail,
        name="demande_detail",
    ),
    # URLs pour l'administration des demandes de télétravail
    path(
        "DemandeTeleTravail/DemandeTeleTravailListView_history_admin/",
        DemandeTeleTravailListView_history_admin.as_view(),
        name="DemandeTeleTravail_list_history_admin",
    ),
    path(
        "DemandeTeleTravail/DemandeTeleTravailListView_Attente_admin/",
        DemandeTeleTravailListView_Attente_admin.as_view(),
        name="DemandeTeleTravail_list_attente_admin",
    ),
    # URLs pour accepter et refuser les demandes
    path(
        "teletravail/accepter/<uuid:demandeTeleTravail_id>/",
        accepter_demande,
        name="accepter_demande",
    ),
    path(
        "teletravail/refuser/<uuid:demandeTeleTravail_id>/",
        refuser_demande,
        name="refuser_demande",
    ),
    # URLs pour les motifs de refus
    path(
        "MotifRefus/MotifRefus_list/", MotifRefuslist.as_view(), name="MotifRefus_list"
    ),
    path(
        "MotifRefus/MotifRefus_create/",
        MotifRefusCreateview.as_view(),
        name="MotifRefus_create",
    ),
    # URL pour afficher le profil utilisateur
    path("user/profil/", user_profile, name="profile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
