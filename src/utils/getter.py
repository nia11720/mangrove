import typing as t


class Getter:
    def __init__(self, data, sep="."):
        self.data = data
        self.sep = sep

    @t.overload
    def get(self, key: None): ...
    @t.overload
    def get(self, key: str): ...
    @t.overload
    def get(self, key: tuple[str]): ...
    @t.overload
    def get(self, key: dict[str]): ...

    def get(self, key):
        if isinstance(self.data, list):
            return [__class__(item, self.sep)[key] for item in self.data]

        if key is None:
            return self.data
        if isinstance(key, str):
            return self._get_from_str(key)
        elif isinstance(key, tuple):
            return [self[k] for k in key]
        elif isinstance(key, set):
            return {k: self[k] for k in key}
        elif isinstance(key, dict):
            return self._get_from_dict(key)

    def __getitem__(self, key):
        return self.get(key)

    def _get_from_str(self, key: str):
        val = self.data
        try:
            for k in key.split(self.sep):
                val = val.get(k)
        except:
            raise KeyError
        else:
            return val

    def _get_from_dict(self, key: dict[str]):
        rv = {}
        getter = self
        for dst, src in key.items():
            if dst.startswith("_"):
                getter = __class__(self[src], self.sep)
                continue
            rv[dst] = getter[src]
        return rv
