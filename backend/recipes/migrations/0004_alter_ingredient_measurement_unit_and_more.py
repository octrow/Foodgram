# Generated by Django 4.2.5 on 2023-10-09 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_amountingredient_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Введите единицу измерения ингредиента', max_length=200, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Введите название ингредиента', max_length=200, verbose_name='Название'),
        ),
        migrations.AlterUniqueTogether(
            name='ingredient',
            unique_together={('name', 'measurement_unit')},
        ),
    ]
