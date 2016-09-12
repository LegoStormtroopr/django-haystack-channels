django-haystack-channels
------------------------

Add asynchronous search index updates to your django app with this drop-in support for django, django-channels and haystack!

1. Install from pip or github
2. Add ``haystack_channels`` to ``INSTALLED_APPS``
3. Update your projects channels routing::

    from channels.routing import route, route_class, include
    from haystack_channels.routing import channel_routing as haystack_channel_routing

    channel_routing = [
      # your routes
      include(haystack_channel_routing)
    ]
4. Update your ``HAYSTACK_SIGNAL_PROCESSOR``::

    HAYSTACK_SIGNAL_PROCESSOR = 'haystack_channels.signals.ChannelsAsyncSignalProcessor'

Or inherit from ``ChannelsAsyncSignalProcessor`` and ``ChannelsAsyncSignalConsumer`` to build a custom version optimised for your app.
