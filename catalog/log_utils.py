from django.db.models.fields.related import ForeignKey
from django.db.models.query_utils import DeferredAttribute


def get_field_value(instance, field, refresh=True):
    """
    Gets the actual value of a field, handling deferred fields and foreign keys.
    """
    if isinstance(field, ForeignKey):
        # For foreign keys, get the ID to avoid unnecessary DB queries
        return getattr(instance, field.attname)

    # If it's a deferred field, force load it
    attr = getattr(instance.__class__, field.name, None)
    if isinstance(attr, DeferredAttribute) and refresh:
        if instance.pk:  # Only refresh if the instance exists in DB
            instance.refresh_from_db(fields=[field.name])

    # Get the current value, whether it's from instance or DB
    return getattr(instance, field.name, field.value_from_object(instance))


def get_model_diff(old, new):
    """
    Compare two model instances and return differences.

    Args:
        old: Original model instance
        new: Updated model instance

    Returns:
        dict: Dictionary of changed fields with (old_value, new_value) tuples
    """
    diff = {}

    for field in new._meta.fields:
        old_value = get_field_value(old, field)
        new_value = get_field_value(new, field, refresh=False)

        # Convert values to comparable types
        if isinstance(old_value, str) or isinstance(new_value, str):
            old_value = str(old_value)
            new_value = str(new_value)

        if old_value != new_value:
            diff[field.name] = (str(old_value), str(new_value))

    return diff
