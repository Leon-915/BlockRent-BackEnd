# Generated by Django 2.1.7 on 2019-03-19 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20190319_0034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appfilter',
            name='end_date',
            field=models.CharField(blank=True, default='', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='appfilter',
            name='start_date',
            field=models.CharField(blank=True, default='', max_length=64),
            preserve_default=False,
        ),
    ]
