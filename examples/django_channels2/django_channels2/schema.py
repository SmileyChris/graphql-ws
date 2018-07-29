import asyncio
import uuid

import graphene
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache

channel_layer = get_channel_layer()


def get_name(info):
    username = getattr(info.context, "session", {}).get("chat-name")
    if username:
        return username
    user = getattr(info.context, "user", None)
    if not user or user.is_anonymous:
        return "anonymous"
    return user.username


class Message(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    message = graphene.String()


class Query(graphene.ObjectType):
    me = graphene.String()
    messages = graphene.List(Message)

    def resolve_me(self, info):
        return get_name(info)

    def resolve_messages(self, info):
        messages = []
        for message in cache.get("demo_messages", []):
            messages.append(Message(**message))
        return messages


class SendMessageMutation(graphene.Mutation):
    class Arguments:
        message = graphene.String(required=True)

    Output = Message

    def mutate(self, info, message):
        data = {"id": uuid.uuid4().hex, "name": get_name(info), "message": message}
        # Store the message (in cache).
        messages = cache.get("demo_messages") or []
        messages.append(data)
        cache.set("demo_messages", messages)
        # Send to subscribers.
        async_to_sync(channel_layer.group_send)("new_message", {"data": data})
        return Message(**data)


class ChangeNameMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    name = graphene.String()

    def mutate(self, info, name):
        info.context.session["chat-name"] = name
        return ChangeNameMutation(name=name)


class Mutations(graphene.ObjectType):
    send_message = SendMessageMutation.Field()
    change_name = ChangeNameMutation.Field()


class Subscription(graphene.ObjectType):
    count_seconds = graphene.Int(up_to=graphene.Int())
    new_message = graphene.Field(Message)

    async def resolve_count_seconds(self, info, up_to=5):
        i = 1
        while i <= up_to:
            yield str(i)
            await asyncio.sleep(1)
            i += 1

    async def resolve_new_message(self, info):
        channel_name = await channel_layer.new_channel()
        await channel_layer.group_add("new_message", channel_name)
        try:
            while True:
                message = await channel_layer.receive(channel_name)
                yield Message(**message["data"])
        finally:
            await channel_layer.group_discard("new_message", channel_name)


schema = graphene.Schema(query=Query, mutation=Mutations, subscription=Subscription)
