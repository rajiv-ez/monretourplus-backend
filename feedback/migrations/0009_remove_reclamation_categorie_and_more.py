# Generated by Django 5.2 on 2025-05-10 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0008_alter_reclamation_statut'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reclamation',
            name='categorie',
        ),
        migrations.RemoveField(
            model_name='avis',
            name='booking_number',
        ),
        migrations.AddField(
            model_name='reclamation',
            name='service_concerne',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='feedback.service'),
        ),
        migrations.DeleteModel(
            name='CategorieReclamation',
        ),
    ]
