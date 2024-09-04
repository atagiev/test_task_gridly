class TableRow:
    """
    Class describes base row in google sheet and gridly table
    Uses the primary key to search for a row in gridly
    """
    def __init__(self, keys: list[str], data: list[str], primary_key: str | None = None):
        assert len(keys) == len(data), f'Keys and data must have same length, keys: {len(keys)}, data: {len(data)}'

        self.primary_key_name = primary_key or keys[0]
        assert self.primary_key_name in keys, f'Primary key {self.primary_key_name} not in {keys}'

        self._keys, self._data = [], []

        for key, value in zip(keys, data):
            if key == self.primary_key_name:
                self.primary_key = value
                continue
            self._keys.append(key)
            self._data.append(value)

    def __eq__(self, other: 'TableRow'):
        return self._keys == other._keys and self._data == other._data

    def __ne__(self, other):
        return not (self == other)

    def to_dict(self) -> dict:
        res = {}
        for key, value in zip(self._keys, self._data):
            res[key] = value
        return res
