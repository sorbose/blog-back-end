# Generated by Django 3.2.5 on 2021-08-24 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bloguser',
            name='avatar',
            field=models.ImageField(default='default.png', upload_to='avatar'),
        ),
    ]
