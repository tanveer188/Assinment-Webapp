# Generated by Django 4.2.3 on 2023-07-14 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_alter_quiz_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='is_done',
            field=models.BooleanField(default=False),
        ),
    ]