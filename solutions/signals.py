"""Signal handlers should go here. Make sure it's loaded..."""

from django.dispatch import receiver
from catalog.models import BookInstance
from django.db.models.signals import pre_save
from logging import getLogger
from django.contrib.auth.signals import user_logged_in
from solutions.models import AuditLog
from catalog.log_utils import get_model_diff, get_field_value

AUDITLOG = getLogger("catalog.audit")


# https://docs.djangoproject.com/en/5.1/ref/signals/
# https://docs.djangoproject.com/en/5.1/ref/contrib/auth/#topics-auth-signals
# EX2: Receive and log changes to BookInstance
@receiver(pre_save, sender=BookInstance)
def log_book_instance_update(sender, instance, **kwargs):
    """For simplicity, just convert any fields to str (may or may not make sense)"""
    old = BookInstance.objects.filter(pk=instance.pk).first()
    if old:

        diff = get_model_diff(old, instance)
        AUDITLOG.info(
            f"Updated {instance}",
            extra={"action": "update", "model": "BookInstance", "diff": diff},
        )
    else:
        # new object
        data = {
            field.name: str(getattr(instance, field.name))
            for field in instance._meta.fields
        }

        AUDITLOG.info(
            f"Created {instance}",
            extra={"action": "create", "model": "BookInstance", "values": data},
        )


# EX2: Receive and log any user logging in
@receiver(user_logged_in)
def log_user_login(user, **kwargs):
    AUDITLOG.info(f"User logged in: {user}")


#  EX4: Add creation of logging records on login and on changes to Users
@receiver(user_logged_in)
def log_user_login(user, **kwargs):
    AuditLog.objects.create(
        user=user, message="User logged in", data={"action": "login"}
    )


# EX4: Bonus - Add creation of logging records  on changes to BookInstance mapped to the user User
@receiver(pre_save, sender=BookInstance)
def log_book_instance_update(sender, instance, **kwargs):
    from .logging import get_user_from_stack

    # NOTE: We could/should pull the same diff as in the previous examples and put into the data member
    old = BookInstance.objects.filter(pk=instance.pk).first()
    if old:
        AuditLog.objects.create(
            user=get_user_from_stack(),
            message="BookInstance updated",
            data={"action": "edit", "pk": str(instance.pk)},
        )
    else:
        # this could be logged after commit
        AuditLog.objects.create(
            user=get_user_from_stack(),
            message="BookInstance created",
            data={"action": "add"},
        )
