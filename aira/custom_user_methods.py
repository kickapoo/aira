from django.contrib.auth.models import User


def is_demo(self):
    if self.username == "demo":
        return True
    return False


User.add_to_class("is_demo", is_demo)
