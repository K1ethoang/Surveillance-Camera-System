from django.apps import AppConfig


class AiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_app'
    
    def ready(self):
        import ai_app.signals
        