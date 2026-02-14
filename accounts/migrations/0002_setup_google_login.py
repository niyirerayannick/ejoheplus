from django.db import migrations

def setup_google_social_app(apps, schema_editor):
    # Get models
    Site = apps.get_model('sites', 'Site')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    
    # Configure Site (ensure site with id=1 exists and is correct)
    # Most local dev environments use 'example.com' as default for ID 1
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={'domain': 'localhost:8000', 'name': 'localhost'}
    )
    if not created:
        site.domain = 'localhost:8000'
        site.name = 'localhost'
        site.save()

    # Configure Google Social App
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google Login',
            'client_id': '1004072849720-mdgifq0vqvgvn25129bd94al4oukupml.apps.googleusercontent.com',
            'secret': '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',
        }
    )
    
    if not created:
        app.client_id = '1004072849720-mdgifq0vqvgvn25129bd94al4oukupml.apps.googleusercontent.com'
        app.secret = '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'
        app.save()
    
    # Link site to app
    app.sites.add(site)

def remove_google_social_app(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    SocialApp.objects.filter(provider='google').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('sites', '0002_alter_domain_unique'), # Default django sites migration
        ('socialaccount', '0001_initial'), # Initial allauth migration
    ]

    operations = [
        migrations.RunPython(setup_google_social_app, remove_google_social_app),
    ]
