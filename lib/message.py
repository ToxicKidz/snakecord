from .bases import (
    BaseObject,
    BaseState
)

from .utils import (
    JsonStructure,
    JsonField,
    JsonArray,
    Snowflake
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .channel import (
        _Channel,
        ChannelState
    )

class MessageType:
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    REPLY = 19
    APPLICATION_COMMAND = 20


class MessageActivity(JsonStructure):
    type: int = JsonField('type')
    party_id: str = JsonField('party_id')


class MessageApplication(BaseObject):
    cover_image: str = JsonField('cover_image')
    description: str = JsonField('description')
    icon: str = JsonField('icon')
    name: str = JsonField('name')


class MessageReference(JsonStructure):
    message_id = JsonField('message_id', int, str)
    channel_id = JsonField('channel_id', int, str)
    guild_id = JsonField('guild_id', int, str)


class MessageActivityType:
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5


class MessageFlag:
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4


class MessageSticker(BaseObject):
    pack_id: int = JsonField('pack_id', int, str)
    name: str = JsonField('name')
    description: str = JsonField('description')
    tags: str = JsonField('tags')
    asset: str = JsonField('asset')
    preview_asset: str = JsonField('preview_asset')
    format_type: int = JsonField('format_type')


class MessageStickerType:
    PNG = 1
    APNG = 2
    LOTTIE = 3


class FollowedChannel(JsonStructure):
    channel_id: int = JsonField('channel_id', int, str)
    webhook_id: int = JsonField('webhook_id', int, str)


class Reaction(JsonStructure):
    count: int = JsonField('count')
    me: bool = JsonField('me')
    # emoji ...


class PermissionOverwrite(BaseObject):
    type: int = JsonField('type')
    allow: int = JsonField('allow', int, str)
    deny: int = JsonField('deny', int, set)


class EmbedType:
    RICH = 'rich'
    IMAGE = 'image'
    VIDEO = 'video'
    GIFV = 'gifv'
    ARTICLE = 'article'
    LINK = 'link'


class EmbedAttachment(JsonStructure):
    url: str = JsonField('url')
    proxy_url = JsonField('proxy_url')
    height = JsonField('height')
    width = JsonField('width')


class EmbedVideo(JsonStructure):
    url: str = JsonField('url')
    height: int = JsonField('height')
    width: int = JsonField('width')


class EmbedProvider(JsonStructure):
    name: str = JsonField('name')
    url: str = JsonField('url')


class EmbedAuthor(JsonStructure):
    name: str = JsonField('name')
    url: str = JsonField('url')
    icon_url: str = JsonField('icon_url')
    proxy_icon_url: str = JsonField('proxy_icon_url')


class EmbedFooter(JsonStructure):
    text: str = JsonField('text')
    icon_url: str = JsonField('icon_url')
    proxy_icon_url: str = JsonField('proxy_icon_url')


class EmbedField(JsonStructure):
    name: str = JsonField('name')
    value: str = JsonField('value')
    inline: bool = JsonField('inline')


class Embed(JsonStructure):
    title: str = JsonField('title')
    type: str = JsonField('type')
    description: str = JsonField('description')
    url: str = JsonField('url')
    # timestamp
    color: int = JsonField('color')
    footer: EmbedFooter = JsonField('footer', struct=EmbedFooter)
    image: EmbedAttachment = JsonField('image', struct=EmbedAttachment)
    thumbnail: EmbedAttachment = JsonField('thumbnail', struct=EmbedAttachment)
    video: EmbedVideo = JsonField('video', struct=EmbedVideo)
    provider: EmbedProvider = JsonField('provider', struct=EmbedProvider)
    author: EmbedAuthor = JsonField('author', struct=EmbedAuthor)
    fields: list = JsonArray('fields', struct=EmbedField)

    def __init__(self, *, title=None, description=None, url=None, color=None):
        self.title = title
        self.description = description
        self.url = url
        self.color = color
        self.fields = []

    def set_footer(self, text=None, icon_url=None, proxy_icon_url=None):
        fields = {
            'text': text,
            'icon_url': icon_url,
            'proxy_icon_url': proxy_icon_url
        }
        self.footer = EmbedFooter.unmarshal(fields)
        return self.footer

    def set_image(self, url=None, proxy_url=None, height=None, width=None):
        fields = {
            'url': url,
            'proxy_url': proxy_url,
            'height': height,
            'width': width
        }
        self.image = EmbedAttachment.unmarshal(fields)
        return self.image

    def set_thumbnail(self, url=None, proxy_url=None, height=None, width=None):
        fields = {
            'url': url,
            'proxy_url': proxy_url,
            'height': height,
            'width': width
        }
        self.thumbnail = EmbedAttachment.unmarshal(fields)
        return self.thumbnail

    def set_video(self, url=None, width=None, height=None):
        fields = {
            'url': url,
            'width': width,
            'height': height
        }
        self.video = EmbedVideo.unmarshal(fields)
        return self.video

    def set_provider(self, name=None, url=None):
        fields = {
            'name': name,
            'url': url
        }
        self.provider = EmbedProvider.unmarshal(fields)
        return self.provider

    def set_author(self, name=None, url=None, icon_url=None, proxy_icon_url=None):
        fields = {
            'name': name,
            'url': url,
            'icon_url': icon_url,
            'proxy_icon_url': proxy_icon_url
        }
        self.author = EmbedAuthor.unmarshal(fields)
        return self.author

    def add_field(self, name, value, inline=False):
        fields = {
            'name': name,
            'value': value,
            'inline': inline
        }
        field = EmbedField.unmarshal(fields)
        self.fields.append(field)
        return field


class MessageAttachment(BaseObject):
    filename: str = JsonField('filename')
    size: int = JsonField('size')
    url: str = JsonField('url')
    proxy_url: str = JsonField('proxy_url')
    height: int = JsonField('height')
    width: int = JsonField('width')


class ChannelMention(BaseObject):
    guild_id: int = JsonField('int', int, str)
    type: int = JsonField('int')
    name: str = JsonField('name')


class AllowedMentionsType:
    ROLES = 'roles'
    USERS = 'users'
    EVERYONE = 'everyone'


class AllowedMentions(JsonStructure):
    parse: list = JsonArray('parse')
    roles: list = JsonArray('roles', int, str)
    users: list = JsonArray('users', int, str)
    replied_user: bool = JsonField('replied_user')


class Message(BaseObject):
    __json_slots__ = (
        'id', 'channel_id', 'guild_id', 'channel', 'guild', '_author', 'author', '_member', 
        'content', 'tts', 'mention_everyone', 'attachments', 'embeds', 'reactions', 'nonce', 
        'pinned', 'webhook_id', 'type', 'activity', 'appliaction', 'flags', 'stickers'
    )

    channel_id: Snowflake = JsonField('channel_id', Snowflake, str)
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    _author = JsonField('author')
    _member = JsonField('member')
    content: str = JsonField('content')
    # timestamp
    # edited_timestamp
    tts: bool = JsonField('tts')
    mention_everyone: bool = JsonField('mention_everyone')
    # mentions
    # mention_roles
    # mention_channels
    attachments: list = JsonArray('attachments', struct=MessageAttachment)
    embeds: list = JsonArray('embeds', struct=Embed)
    reactions: list = JsonArray('reactions', struct=Reaction)
    nonce = JsonField('nonce')
    pinned: bool = JsonField('pinned')
    webhook_id: int = JsonField('webhook_id', int, str)
    type: int = JsonField('type')
    activity: MessageActivity = JsonField('activity', struct=MessageActivity)
    application: MessageApplication = JsonField('application')
    # message_reference
    flags: int = JsonField('flags')
    stickers: list = JsonArray('stickers', struct=MessageSticker)

    # referenced_message

    def __init__(self, *, state: 'ChannelState', channel: '_Channel'):
        self._state = state

        self.channel = channel

        if self.channel is not None:
            self.guild = self.channel.guild
        else:
            self.guild = state._client.guilds.get(self.guild_id)

        if self.guild is not None:
            if self._member.get('user') is None:
                self._member['user'] = self._author
            self.author = self.guild.members.add(self._member)
        else:
            self.author = state._client.users.add(self._author)

        del self._author
        del self._member


class MessageState(BaseState):
    def __init__(self, client, channel: '_Channel'):
        super().__init__(client)
        self._channel = channel

    def add(self, data) -> Message:
        message = self.get(data['id'])
        if message is not None:
            message._update(data)
            return message
        message = Message.unmarshal(data, state=self, channel=self._channel)
        self._values[message.id] = message
        return message

    async def fetch(self, message_id) -> Message:
        data = await self._client.rest.get_channel_message(self._channel.id)
        return self.add(data)