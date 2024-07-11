# Generated by Django 5.0.3 on 2024-04-29 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_demandeteletravail_lieu_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demandeteletravail',
            name='motif',
            field=models.CharField(choices=[('Necessite_professionnelle', 'Nécessité professionnelle'), ('Conditions_env_defavorables', 'Conditions environnementales défavorables'), ('Perturbations_sociales_transp', 'Perturbations sociales et de transport'), ('Cas_de_force_majeure', 'Cas de force majeure'), ('Demandes_personnelles_exceptionnelles', 'Demandes personnelles exceptionnelles'), ('Autres', 'Autres')], max_length=50),
        ),
        migrations.AlterField(
            model_name='demandeteletravail',
            name='statut',
            field=models.CharField(choices=[('en attente', 'En attente'), ('Refusé', 'Refusé'), ('Accepté', 'Accepté')], default='en attente', editable=False, max_length=10),
        ),
    ]
