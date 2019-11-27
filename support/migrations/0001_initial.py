# Generated by Django 2.0.12 on 2019-10-27 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='for_support_purposes', to='project.Project')),
            ],
        ),
    ]
