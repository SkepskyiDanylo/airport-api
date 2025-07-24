import os

from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from airport.models import Airplane


@receiver(pre_save, sender=Airplane)
def airplane_save_handler(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.image and (instance.image != old_instance.image):
            instance.image.delete(save=False)
    except sender.DoesNotExist:
        pass


@ receiver(post_delete, sender=Airplane)
def airplane_delete_handler(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)