# Generated by Django 4.2 on 2023-04-19 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laundApp', '0009_alter_category_updateddate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='services',
            name='createdBy',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]