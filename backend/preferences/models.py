from django.conf import settings
from django.db import models

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.CharField(max_length=64, default='light')
    last_project_id = models.IntegerField(null=True, blank=True)
    window_bounds = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Prefs<{self.user_id}>"
