# Generated by Django 4.2.3 on 2023-07-18 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0009_quiz_avg_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('visit_date', models.DateField()),
                ('visit_time', models.TimeField()),
                ('url_name', models.CharField(max_length=255)),
                ('visited_url', models.URLField()),
            ],
        ),
    ]
