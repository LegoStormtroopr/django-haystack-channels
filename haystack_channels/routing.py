from channels.routing import route, route_class

channel_routing = [
    route_class("haystack_channels.signals.ChannelsAsyncSignalConsumer"),
]
