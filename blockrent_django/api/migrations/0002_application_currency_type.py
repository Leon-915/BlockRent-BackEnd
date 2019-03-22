# Generated by Django 2.1.7 on 2019-03-21 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='currency_type',
            field=models.CharField(blank=True, choices=[('AED', 'AED'), ('USD', 'USD'), ('GBP', 'GBP'), ('AUD', 'AUD')], max_length=32),
        ),
    ]