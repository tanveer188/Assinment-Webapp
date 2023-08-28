from django.apps import apps
from django.contrib import admin

# Get the "teacher" app's models
teacher_app = apps.get_app_config('teacher')
teacher_models = teacher_app.get_models()

# Register the "teacher" app's models with the admin site
for model in teacher_models:
    admin.site.register(model)
