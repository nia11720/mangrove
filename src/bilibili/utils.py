from hashlib import md5


def attach_wrid(params: str):
    sorted_params = "&".join(sorted(params.split("&")))
    w_rid = md5(f"{sorted_params}ea1db124af3c7062474693fa704f4ff8".encode()).hexdigest()

    return f"{params}&w_rid={w_rid}"


class DanmakuParser:
    def __init__(self, stream: bytes):
        self.stream = stream
        self.pos = 0

    def read(self, n=1):
        b = self.stream[self.pos : self.pos + n]
        if len(b) == n:
            self.pos += len(b)
        else:
            raise EOFError

        return b

    def read_unit8(self):
        return ord(self.read(1))

    def read_uint32(self):
        uint32 = 0
        for i in range(0, 32, 7):
            uint8 = self.read_unit8()
            uint32 |= (uint8 & 0x7F) << i
            if not uint8 >> 7:
                break
        else:
            self.read(5)

        return uint32 & 0xFFFF_FFFF

    def read_string(self):
        n = self.read_uint32()
        return self.read(n).decode()

    def skip(self, t: int):
        match t & 0x07:
            case 0:
                while self.read_unit8() & 0x80:
                    pass
            case 1:
                self.read(8)
            case 2:
                n = self.read_uint32()
                self.read(n)
            case 3:
                while True:
                    t = self.read_uint32()
                    if t & 0x07 == 4:
                        break

                    self.skip(t)
            case 5:
                self.read(4)

    def __iter__(self):
        while True:
            try:
                yield self.read_uint32()
            except EOFError:
                break

    def decode_item(self):
        n = self.read_uint32()
        stream = self.__class__(self.read(n))

        item = {}
        for t in stream:
            match t >> 3:
                case 2:
                    item["stime"] = stream.read_uint32()
                case 3:
                    item["mode"] = stream.read_uint32()
                case 4:
                    item["size"] = stream.read_uint32()
                case 5:
                    item["color"] = stream.read_uint32()
                case 6:
                    item["uhash"] = stream.read_string()
                case 7:
                    item["text"] = stream.read_string()
                case 8:
                    item["date"] = stream.read_uint32()
                case 9:
                    item["weight"] = stream.read_uint32()
                case 10:
                    item["action"] = stream.read_string()
                case 11:
                    item["pool"] = stream.read_uint32()
                case 12:
                    item["dmid"] = stream.read_string()
                case 13:
                    item["attr"] = stream.read_uint32()
                case 22:
                    item["animation"] = stream.read_string()
                case 24:
                    item["colorful"] = stream.read_uint32()
                case _:
                    stream.skip(t)

        return item

    def decode_colorful(self):
        n = self.read_uint32()
        stream = self.__class__(self.read(n))

        for t in stream:
            match t >> 3:
                case 1:
                    type = stream.read_uint32()
                case 2:
                    src = stream.read_string()
                case _:
                    stream.skip(t)

        return (type, src)

    def decode(self):
        items = []
        colorfuls = []
        for t in self:
            match t >> 3:
                case 1:
                    items.append(self.decode_item())
                case 5:
                    colorfuls.append(self.decode_colorful())
                case _:
                    self.skip(t)

        colorfuls = dict(colorfuls)
        for item in items:
            type = item.get("corlorful")
            if type is not None:
                item["colorful_img"] = colorfuls[type]

        return {"items": items}
