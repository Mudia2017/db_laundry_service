# Generated by Django 4.2 on 2023-04-19 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laundApp', '0007_category_alter_companyregisterform_lastlogin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='services',
            name='updatedDate',
            field=models.DateTimeField(blank=True),
        ),
    ]
