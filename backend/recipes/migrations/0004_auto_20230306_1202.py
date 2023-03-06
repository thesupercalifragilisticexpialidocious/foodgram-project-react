# Generated by Django 2.2.19 on 2023-03-06 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20230306_1157'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'unit'), name='unique_ingredient_name_unit_relation'),
        ),
    ]
