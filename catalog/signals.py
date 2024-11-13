"""Signal handlers should go here. Make sure it's loaded..."""

from django.dispatch import receiver
from catalog.models import BookInstance


# https://docs.djangoproject.com/en/5.1/ref/signals/
# https://docs.djangoproject.com/en/5.1/ref/contrib/auth/#topics-auth-signals
# TODO EX2: Receive and log changes to BookInstance
# TODO EX2: Receive and log any user logging in


# TODO EX4: Add creation of logging records on login


# TODO EX4: Bonus - Add creation of logging records  on changes to BookInstance mapped to the user User
