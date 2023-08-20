from abc import ABC, abstractmethod


class TextHistory:
    def __init__(self, text=None):
        if text is None:
            text = ''
        self._text = text
        self._version = 0
        self._data = []

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def insert(self, text, pos=None):
        if pos is None:
            pos = len(self.text)
        elif pos < 0 or pos > len(self.text):
            raise ValueError('Wrong position')

        action = InsertAction(text, pos, self.version, self.version + 1)

        return self.action(action)

    def replace(self, text, pos=None):
        if pos is None:
            pos = len(self.text)
        elif pos < 0 or pos > len(self.text):
            raise ValueError('Wrong position')

        action = ReplaceAction(text, pos, self.version, self.version + 1)

        return self.action(action)

    def delete(self, pos, length):
        if pos < 0 or pos > len(self.text) or (pos + length) > len(self.text):
            raise ValueError('Wrong position or length')

        action = DeleteAction(pos, length, self.version, self.version + 1)

        return self.action(action)

    def action(self, action):
        if action.from_version >= action.to_version or action.from_version < 0:
            raise ValueError('Wrong version value')
        self._text = action.apply(self.text)
        self._version = action.to_version
        self._data.append(action)
        return action.to_version

    def get_actions(self, from_version=None, to_version=None):
        if from_version is None:
            from_version = 0
        if to_version is None:
            to_version = self.version

        if from_version < 0 or from_version > to_version:
            raise ValueError('Wrong version value')

        if to_version > self.version:
            raise ValueError('Wrong range')

        return ([act for act in self._data
                 if from_version <= act.from_version
                 and act.to_version <= to_version]
                )


# ABC - Abstract Base Class
class Action(ABC):
    def __init__(self, pos, from_version, to_version):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    def __repr__(self):
        return '{!r}'.format(self.__class__)

    @abstractmethod
    def apply(self, string):
        pass


class InsertAction(Action):
    """
    Attributes:
        text - text to insert
    """
    def __init__(self, text, pos, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    # принимает строку и возвращает модифицированную строку
    def apply(self, string):
        return string[:self.pos] + self.text + string[self.pos:]


class ReplaceAction(Action):
    """
    Attributes:
        text - text to replace
    """
    def __init__(self, text, pos, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def apply(self, string):
        return (string[:self.pos]
                + self.text + string[self.pos + len(self.text):]
                )


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.length = length

    def apply(self, string):
        return string[:self.pos] + string[self.pos + self.length:]
