"""Map model writes to live portal events (see accounts.realtime)."""

from django.db.models.signals import post_delete, post_save

from .realtime import broadcast


def _actor(instance):
    return getattr(instance, 'updated_by_id', None) or getattr(instance, 'created_by_id', None)


def _sale_saved(sender, instance, created, **kwargs):
    text = f'Yeni satış: {instance.number}' if created else ''
    broadcast('sales', actor_id=_actor(instance), text=text, obj_id=instance.pk)


def _sale_deleted(sender, instance, **kwargs):
    broadcast('sales', actor_id=None, obj_id=instance.pk)


def _payment_saved(sender, instance, created, **kwargs):
    if created:
        broadcast('sales', actor_id=getattr(instance, 'created_by_id', None), obj_id=None)


def _job_saved(sender, instance, created, **kwargs):
    text = f'Yeni servis işi: {instance.number}' if created else ''
    broadcast('jobs', actor_id=_actor(instance), text=text, obj_id=instance.pk)


def _job_deleted(sender, instance, **kwargs):
    broadcast('jobs', actor_id=None, obj_id=instance.pk)


def _movement_saved(sender, instance, created, **kwargs):
    if created:
        broadcast('stock', actor_id=getattr(instance, 'created_by_id', None), obj_id=instance.product_id)


def _device_saved(sender, instance, **kwargs):
    broadcast('maintenance', actor_id=getattr(instance, 'created_by_id', None), obj_id=instance.pk)


def connect_live_signals():
    from sales.models import Payment, Sale
    from service.models import Device, Job
    from stock.models import StockMovement

    post_save.connect(_sale_saved, sender=Sale, dispatch_uid='live-sale-save')
    post_delete.connect(_sale_deleted, sender=Sale, dispatch_uid='live-sale-delete')
    post_save.connect(_payment_saved, sender=Payment, dispatch_uid='live-payment-save')
    post_save.connect(_job_saved, sender=Job, dispatch_uid='live-job-save')
    post_delete.connect(_job_deleted, sender=Job, dispatch_uid='live-job-delete')
    post_save.connect(_movement_saved, sender=StockMovement, dispatch_uid='live-movement-save')
    post_save.connect(_device_saved, sender=Device, dispatch_uid='live-device-save')
    post_delete.connect(_device_saved, sender=Device, dispatch_uid='live-device-delete')
