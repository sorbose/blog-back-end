# Generated by Django 3.2.5 on 2021-08-29 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0010_alter_comment_touser'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='comment_num',
            field=models.IntegerField(default=0),
        ),
    ]
