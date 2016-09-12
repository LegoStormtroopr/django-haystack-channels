# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.apps import apps
from django.db import models

from channels import Channel
from channels.generic import BaseConsumer

from haystack import connections
from haystack.constants import DEFAULT_ALIAS
from haystack.signals import BaseSignalProcessor


def construct_message(instance):
    return {
            'pk':instance.pk,
            'app_label':instance._meta.app_label,
            'model_name':instance._meta.model_name,
        }

class ChannelsRealTimeAsyncSignalProcessor(BaseSignalProcessor):
    """
    Allows for observing when saves/deletes fire & automatically updates the
    search engine appropriately.
    """

    def setup(self):
        # Naive (listen to all model saves).
        models.signals.post_save.connect(self.async_save)
        models.signals.post_delete.connect(self.async_delete)
        # Efficient would be going through all backends & collecting all models
        # being used, then hooking up signals only for those.

    def teardown(self):
        # Naive (listen to all model saves).
        models.signals.post_save.disconnect(self.async_save)
        models.signals.post_delete.disconnect(self.async_delete)
        # Efficient would be going through all backends & collecting all models
        # being used, then disconnecting signals only for those.

    def async_save(self, sender, instance, **kwargs):
        Channel("haystack_channels.item.saved").send(construct_message(instance))

    def async_delete(self, sender, instance, **kwargs):
        Channel("haystack_channels.item.deleted").send(construct_message(instance))


class ChannelsAsyncSignalConsumer(BaseConsumer):
    method_mapping = {
        'haystack_channels.item.saved': "async_save_caught",
        "haystack_channels.item.deleted": "async_delete_caught",
    }

    def get_index(self, sender):
        return connections[DEFAULT_ALIAS].get_unified_index().get_index(sender)
    
    def get_instance(self, sender, pk):
        return sender.objects.filter(pk=pk).first()

    def get_sender(self, app_label, model_name):
        return apps.get_model(app_label, model_name)

    def async_save_caught(self, message, **kwargs):
        sender = self.get_sender(message['app_label'], message['model_name'])
        instance = self.get_instance(sender, message['pk'])
        if instance:
            index = self.get_index(sender)
            index.update_object(instance) #, using=using)

    def async_delete_caught(self, message, **kwargs):
        sender = self.get_sender(message['app_label'], message['model_name'])
        instance = sender.filter(pk=message['pk']).first()
        if instance:
            index = self.get_index(sender)
            index.remove_object(instance) #, using=using)
