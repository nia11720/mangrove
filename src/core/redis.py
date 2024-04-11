import re
import pickle as picklelib
import json as jsonlib

from redis.connection import ConnectionPool
from redis.client import Redis as _Redis, Pipeline as _Pipeline, PubSub as _PubSub

from .config import REDIS_URL
from . import commands as COMMANDS

import typing as t

if t.TYPE_CHECKING:
    _Redis = _Redis[str]
    _Pipeline = _Pipeline[str]


def add_prefix(cmd_args: list, prefix=""):
    cmd, *args = cmd_args
    cmd = re.sub(r"[ -]", "_", cmd)

    if not hasattr(COMMANDS, cmd):
        return cmd_args

    idx = getattr(COMMANDS, cmd)
    if idx is None:
        raise NotImplementedError
    elif isinstance(idx, int):
        numkeys = args[idx - 1]
        idx = (idx, idx + numkeys, 1)

    for i, key in list(enumerate(args))[slice(*idx)]:
        assert isinstance(key, str)
        if not key.startswith(f"@"):
            args[i] = re.sub(r"(?<=[@:]):", "", f"@{prefix}:{key}")

    return [cmd_args[0], *args]


class NamespaceMixin:
    def __init__(self, *args, **kwargs):
        self.namespace = kwargs.pop("namespace", "")
        super().__init__(*args, **kwargs)

    def execute_command(self, *args, **kwargs):
        args = add_prefix(args, f"mangrove:{self.namespace}")
        return super().execute_command(*args, **kwargs)


class CommandMixin:
    @t.overload
    def set(
        self,
        key,
        value,
        json=False,
        pickle=False,
        ex=None,
        px=None,
        nx=False,
        xx=False,
        keepttl=False,
        get=False,
        exat=None,
        pxat=None,
    ): ...

    def set(self, key, value, json=False, pickle=False, **kwargs):
        if json:
            value = jsonlib.dumps(value, separators=(",", ":"))
        elif pickle:
            value = picklelib.dumps(value)
        return super().set(key, value, **kwargs)

    def get(self, key, json=False, pickle=False):
        if json:
            data = super().get(key)
            if data:
                return jsonlib.loads(data)
        elif pickle:
            data = super().execute_command("GET", key, NEVER_DECODE=True)
            if data:
                return picklelib.loads(data)
        else:
            return super().get(key)


connection_pool = ConnectionPool.from_url(url=REDIS_URL, decode_responses=True)


class Redis(CommandMixin, NamespaceMixin, _Redis):
    def __init__(self, namespace=""):
        super().__init__(connection_pool=connection_pool, namespace=namespace)

    def pipeline(self, transaction=True, shard_hint=None):
        return Pipeline(
            self.connection_pool,
            self.response_callbacks,
            transaction,
            shard_hint,
            namespace=self.namespace,
        )

    def pubsub(self, **kwargs):
        return PubSub(self.connection_pool, namespace=self.namespace, **kwargs)


class Pipeline(CommandMixin, NamespaceMixin, _Pipeline):
    pass


class PubSub(NamespaceMixin, _PubSub):
    pass
