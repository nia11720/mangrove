import os
import json as jsonlib

import httpx


class Argument:
    def __init__(
        self,
        name: str,
        type: str,
        optional=False,
        multiple=False,
        multiple_token=False,
        token: str | None = None,
        arguments=(),
        **kwargs,
    ):
        self.name = name
        self.type = type
        self.optional = optional
        self.multiple = multiple
        self.multiple_token = multiple_token
        self.token = token
        self.arguments = [__class__(**i) for i in arguments]

        if multiple_token and self.type == "block":
            token = __class__(name=token.lower(), type="pure-token", token=token)
            self.arguments.insert(0, token)
            self.token = None

    def is_position_arg(self):
        match self.type:
            case "oneof":
                return all(map(lambda i: i.is_position_arg(), self.arguments))
            case "block":
                return False
            case _:
                return not self.optional and not self.multiple

    def is_key(self):
        return self.type in ["key", "pattern"] or self.name == "channel"

    def has_key(self):
        if self.type in ["oneof", "block"]:
            return any(map(lambda i: i.is_key() or i.has_key(), self.arguments))
        else:
            return False

    def to_string(self):
        match self.type:
            case "pure-token":
                return ""
            case "oneof":
                return f"<{'|'.join(map(str, self.arguments))}>"
            case "block":
                return f"{{{' '.join(map(str, self.arguments))}}}"
            case _:
                prefix = "@@@" if self.is_key() else ""
                return f"{prefix}{self.name}"

    def __str__(self):
        prefix = self.token or ""
        to_str = self.to_string()
        sep = " " if prefix and to_str else ""
        suffix = ["", "?", "+", "*"][self.multiple << 1 | self.optional]

        return f"{prefix}{sep}{to_str}{suffix}"


class Command(Argument):
    def __init__(self, config: tuple[str, dict]):
        name, command = config
        kwargs = {
            "name": name.translate(str.maketrans(" -", "__")),
            "type": "block",
            "token": name,
            "multiple_token": True,
            "arguments": command.get("arguments", []),
        }
        super().__init__(**kwargs)

    def parse_key(self):
        if self.name in ["MSET", "MSETNX"]:
            return (0, None, 2)

        args = self.arguments[1:]
        keys: list[tuple[int, Argument]] = []

        for i, arg in enumerate(args):
            if arg.has_key():
                return
            if arg.is_key():
                keys.append((i, arg))

        if len(keys) == 1:
            ((i, key),) = keys
            if key.is_position_arg():
                return (i, i + 1, 1)
            elif key.multiple and i > 0 and args[i - 1].name == "numkeys":
                for arg in args[0 : i - 1]:
                    if not arg.is_position_arg():
                        return
                else:
                    return i
        elif len(keys) == 2:
            (i0, key0), (i1, key1) = keys
            if i0 + 1 == i1 and key0.is_position_arg() and key1.is_position_arg():
                return (i0, i0 + 2, 1)

        if len(keys) == len(args):
            return (0, None, 1)
        elif len(keys) + 1 == len(args):
            if not args[0].is_key() and args[0].is_position_arg():
                return (1, None, 1)
            elif not args[-1].is_key() and args[-1].is_position_arg():
                return (0, -1, 1)

    def __str__(self):
        return super().__str__()[1:-1]


cache = ".cache/redis-command"
os.makedirs(cache, exist_ok=True)


def load_commands():
    path = f"{cache}/commands.json"
    url = "https://raw.githubusercontent.com/redis/redis-doc/master/commands.json"

    if not os.path.exists(path):
        res = httpx.get(url)
        with open(path, "w") as fp:
            print(res.text, file=fp)

    with open(path) as fp:
        commands: dict = jsonlib.load(fp)
        return map(Command, commands.items())


def main():
    fp_all = open(f"{cache}/syntax.all.txt", "w")
    fp_key = open(f"{cache}/syntax.key.txt", "w")
    fp_unknown = open(f"{cache}/syntax.unknown.txt", "w")

    unknown: list[str] = []
    registry: dict[tuple | int, list[str]] = {}

    for cmd in load_commands():
        print(cmd, file=fp_all)

        if cmd.has_key():
            idx = cmd.parse_key()
            print(cmd, idx, file=fp_key, sep="\n")

            if idx is None:
                print(cmd, file=fp_unknown)
                unknown.append(cmd.name)
            else:
                registry.setdefault(idx, []).append(cmd.name)

    fp_all.close()
    fp_key.close()
    fp_unknown.close()

    def sort_key(key: int | tuple[int | None, ...]):
        if isinstance(key, int):
            return (1, key)
        else:
            return (0, [(100 if i is None else i) for i in key])

    with open("src/core/commands.py", "w") as fp:
        for key in sorted(registry, key=sort_key):
            cmds = registry[key]

            for cmd in cmds:
                print(f"{cmd} = {key}", file=fp)
            print("", file=fp)

        for cmd in unknown:
            print(f"{cmd} = None", file=fp)


if __name__ == "__main__":
    main()
