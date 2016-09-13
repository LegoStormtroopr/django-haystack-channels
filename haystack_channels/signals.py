# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

from django.apps import apps
from django.db import models

from channels import Channel
from channels.generic import BaseConsumer

from haystack import connections
from haystack.constants import DEFAULT_ALIAS
from haystack.exceptions import NotHandled
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
        if instance._meta.app_label == 'migrations':
            # Migrations send a whole lot of signals in too short a period
            # Migrations aren't an installed app, so they cause us grief
            return
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
        try:
            return apps.get_model(app_label, model_name)
        except:
            return None

    def async_save_caught(self, message, **kwargs):
        sender = self.get_sender(message['app_label'], message['model_name'])
        print(sender)
        if sender:
            instance = self.get_instance(sender, message['pk'])
            if instance:
                try:
                    index = self.get_index(sender)
                    index.update_object(instance) #, using=using)
                except NotHandled:
                    # TODO: Maybe log it or let the exception bubble?
                    pass

    def async_delete_caught(self, message, **kwargs):
        sender = self.get_sender(message['app_label'], message['model_name'])
        if sender:
            instance = self.get_instance(sender, message['pk'])
            if instance:
                try:
                    index = self.get_index(sender)
                    index.remove_object(instance) #, using=using)
                except NotHandled:
                    # TODO: Maybe log it or let the exception bubble?
                    pass
