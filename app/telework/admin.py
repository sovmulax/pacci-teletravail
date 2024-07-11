from django.contrib import admin
from django.contrib import messages
from .models import TypePersonnel, Service, Personnel, DemandeTeleTravail, LiaisonAgentSuperieur,MotifRefus

class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_personnel', 'service','email')




class DemandeTeleTravailAdmin(admin.ModelAdmin):
    list_display = ('agent', 'motif', 'date_debut', 'date_fin', 'lieu', 'statut', 'date_demande', 'date_signature_superieur','motif_refus')
    search_fields = ('agent__user__username', 'lieu')
 

    actions = ['accepter_demandes', 'refuser_demandes']

    def accepter_demandes(self, request, queryset):
        for demande in queryset:
            try:
                superieur = LiaisonAgentSuperieur.objects.get(agent=demande.agent).superieur
                if request.user == superieur.user:
                    demande.accepter_demande(superieur)
                    messages.success(request, f"La demande de {demande.agent.user.username} a été acceptée.")
            except LiaisonAgentSuperieur.DoesNotExist:
                messages.error(request, f"No linked superior found for agent {demande.agent.user.username}.")

    def refuser_demandes(self, request, queryset):
        for demande in queryset:
            try:
                superieur = LiaisonAgentSuperieur.objects.get(agent=demande.agent).superieur
                if request.user == superieur.user:
                    demande.refuser_demande(superieur)
                    messages.success(request, f"La demande de {demande.agent.user.username} a été refusée.")
            except LiaisonAgentSuperieur.DoesNotExist:
                messages.error(request, f"No linked superior found for agent {demande.agent.user.username}.")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(agent__user=request.user)
        return qs

class LiaisonAgentSuperieurAdmin(admin.ModelAdmin):
    list_display = ('agent', 'superieur')

admin.site.register(TypePersonnel)
admin.site.register(MotifRefus)
admin.site.register(Service)
admin.site.register(Personnel, PersonnelAdmin)
admin.site.register(DemandeTeleTravail, DemandeTeleTravailAdmin)
admin.site.register(LiaisonAgentSuperieur, LiaisonAgentSuperieurAdmin)
