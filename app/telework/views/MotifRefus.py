from urllib import request
from django.views import View, generic
from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse_lazy,reverse
from telework.models import Personnel, MotifRefus,LiaisonAgentSuperieur
from telework.forms import  MotifRefusForm
from braces.views import FormMessagesMixin
from django.views.generic import ListView,CreateView,UpdateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.http import JsonResponse

@method_decorator(login_required, name='dispatch')
class MotifRefuslist(ListView):
    
    model = MotifRefus
    context_object_name = 'MotifRefus_list'
    template_name = "pages/motif_refus/motif_refus_list.html"

    def get_queryset(self):
        queryset = MotifRefus.objects.all() 
        return queryset
    


class MotifRefusCreateview(FormMessagesMixin, CreateView):
    
    model=MotifRefus
    form_class=MotifRefusForm
    template_name="pages/motif_refus/MotifRefus_create.html"
    success_url = reverse_lazy('DemandeTeleTravail_list_history_admin')
    form_invalid_message="Oups, quelque chose s'est mal passé!"
    
   
    
    def get_form_valid_message(self):
        return u"{0} Transaction ajouté avec succès!".format(self.object.name)
    
    def get_form_error_message(self):
        return u"Une erreur s'est produite lors de la création de {0}.".format(self.object.name)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        print(f"motif refus  Post : {request.POST}")
        form = MotifRefusForm(request.POST)
        if form.is_valid():
            """user = self.request.user
            motif=form.cleaned_data['motif']
            print(motif)
            
            personnel = Personnel.objects.filter(user=user).first()
            
            mail = personnel.email
            print(f"L'adresse e-mail de superieur  est : {mail}")
           
                
            personnels = Personnel.objects.get(user=self.request.user)
            
            liaison_agent = LiaisonAgentSuperieur.objects.filter(agent=personnels).first()
            
            if liaison_agent:
                 # Récupérer l'adresse e-mail du supérieur hiérarchique
                superieur_email = liaison_agent.superieur.email
                # Faites quelque chose avec l'adresse e-mail du supérieur, par exemple, l'utiliser pour envoyer un e-mail
                print(f"L'adresse e-mail du supérieur hiérarchique est : {superieur_email}")

                # Envoyer un e-mail à l'utilisateur
                subject_user = 'Demande de télétravail refusée'
                message_user = 'Votre demande de télétravail a été refusée voici le motif de refus :.'
                send_mail(subject_user, message_user, 'ibrahimkabore025@gmail.com', [mail])

                # Envoyer un e-mail au supérieur hiérarchique
                subject_superieur = 'télétravail refus'
                message_superieur = f'le mail avec le motif de refus a ete ete envoyer.'
                send_mail(subject_superieur, message_superieur, 'ibrahimkabore025@gmail.com', [mail])
            else:
                print("Aucune liaison d'agent supérieur trouvée pour cet utilisateur.")"""
            form.save()
            messages.error(request, f" Un mail a été envoyé à la personne concernée avec le Motif de Refus énoncée ")
            return HttpResponseRedirect(reverse('DemandeTeleTravail_list_history_admin'),{"form": form})
        else:
          
            print(f"DemandeTeleTravail form errors : {form.errors}")
            return HttpResponseRedirect(reverse('DemandeTeleTravail_list_history_admin'))


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context['form'] = MotifRefusForm()
        context['method'] = "post"
        return context