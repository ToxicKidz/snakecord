from typing import Any, Dict, Optional, TypeVar
from .baseobject import BaseObject
from .guildobject import Guild
from .userobject import User
from ..utils import JsonTemplate

_GT = TypeVar('_GT', bound='GuildTemplate')

GuildTemplateTemplate: JsonTemplate

class GuildTemplate(BaseObject[str]):
    @property
    def code(self) -> str: ...
    @property
    def creator(self) -> Optional[User]: ...
    @property
    def source_guild(self) -> Optional[Guild]: ...
    async def fetch(self: _GT) -> _GT: ...
    async def create_guild(self) -> Guild: ...
    async def sync(self: _GT) -> _GT: ...
    async def modify(self: _GT) -> _GT: ...
    async def delete(self) -> None: ...
    def update(self, data: Dict[str, Any], *args: Any, **kwargs: Any) -> None: ...
