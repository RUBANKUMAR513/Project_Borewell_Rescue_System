# Generated by Django 5.0.4 on 2024-04-06 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RescueOperations', '0002_devicedetails_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicedetails',
            name='state',
            field=models.CharField(default='off', max_length=100),
        ),
    ]
