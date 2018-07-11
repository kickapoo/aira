from django.apps import AppConfig

class AiraConfig(AppConfig):
    name = 'aira'
    verbose_name = "Aira"

    def ready(self):
        print("Fdafds")
        pass # startup code here
