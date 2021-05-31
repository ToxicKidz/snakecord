from typing import Any, Optional

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .templateobject import GuildTemplate as _GuildTemplate
from .userobject import User
from ..states.guildstate import GuildState
from ..utils import JsonObject, JsonTemplate, Snowflake

GuildPreviewTemplate: JsonTemplate = ...
GuildTemplate: JsonTemplate = ...

class Guild(BaseObject[Snowflake]):
    def __init__(self, *, state: GuildState) -> None: ...
    async def modify(self, **kwargs: Any) -> Guild: ...
    async def delete(self) -> None: ...
    async def prune(self, **kwargs: Any) -> Optional[int]: ...
    async def preview(self) -> Guild: ...
    async def voice_regions(self) -> list[dict[str, Any]]: ...
    async def invites(self) -> list[dict[str, Any]]: ...
    async def templates(self) -> list[_GuildTemplate]: ...
    async def create_template(self, **kwargs: Any) -> _GuildTemplate: ...
    def to_preview_dict(self) -> dict[str, Any]: ...
    def update(self, data: dict[str, Any], *args: Any, **kwargs: Any) -> None: ...

GuildBanTemplate: JsonTemplate = ...

class GuildBan(BaseObject[Snowflake]):
    guild: Guild
    user: User
    def __init__(self, *, state: GuildState, guild: Guild) -> None: ...
    def update(self, data: dict[str, Any], *args: Any, **kwargs: Any) -> None: ...

WelcomeScreenChannelTemplate: JsonTemplate = ...

class WelcomeScreenChannel(JsonObject):
    guild: Guild
    def __init__(self, *, guild: Guild) -> None: ...
    @property
    def channel(self) -> GuildChannel: ...
    @property
    def emoji(self) -> None: ...