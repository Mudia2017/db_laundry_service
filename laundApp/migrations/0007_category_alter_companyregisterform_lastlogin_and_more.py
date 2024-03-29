# Generated by Django 4.2 on 2023-04-19 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('laundApp', '0006_companyregisterform_termscondition'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catName', models.CharField(blank=True, default='', max_length=200)),
                ('createdDate', models.DateTimeField(auto_now_add=True)),
                ('updatedDate', models.DateTimeField(blank=True, default='')),
                ('updatedBy', models.CharField(blank=True, default='', max_length=200)),
                ('active', models.BooleanField(default=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='companyregisterform',
            name='lastLogin',
            field=models.DateTimeField(blank=True, default=''),
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serviceName', models.CharField(blank=True, default='', max_length=200)),
                ('ironNormal', models.CharField(blank=True, default='', max_length=200)),
                ('ironFast', models.CharField(blank=True, default='', max_length=200)),
                ('laundryNormal', models.CharField(blank=True, default='', max_length=200)),
                ('laundryFast', models.CharField(blank=True, default='', max_length=200)),
                ('laundryIronNormal', models.CharField(blank=True, default='', max_length=200)),
                ('laundryIronFast', models.CharField(blank=True, default='', max_length=200)),
                ('dryWashNormal', models.CharField(blank=True, default='', max_length=200)),
                ('dryWashFast', models.CharField(blank=True, default='', max_length=200)),
                ('stainRemoval', models.CharField(blank=True, default='', max_length=200)),
                ('dryUp', models.CharField(blank=True, default='', max_length=200)),
                ('others', models.CharField(blank=True, default='', max_length=200)),
                ('createdDate', models.DateTimeField(auto_now_add=True)),
                ('updatedDate', models.DateTimeField(blank=True, default='')),
                ('updatedBy', models.CharField(blank=True, default='', max_length=200)),
                ('active', models.BooleanField(default=True, null=True)),
                ('categoryId', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='laundApp.category')),
                ('comProfileField', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='laundApp.companyregisterform')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='comProfileField',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='laundApp.companyregisterform'),
        ),
    ]
