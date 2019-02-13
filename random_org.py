from rdoclient_py3 import RandomOrgClient


class Random:
    def item(self, items):
        max = Random._get_max(items)
        pos = self._get_integer(max)
        return items[pos]

    def items(self, items, n, replacement=False):
        max = Random._get_max(items)
        integers = self._get_integers(n, max, replacement=replacement)
        set = [items[i] for i in integers]
        return set

    def _get_integer(self, max=0, min=0):
        if min is max:
            return max
        integers = self._get_integers(min=min, max=max)
        return integers[0]

    def _get_integers(self, n=1, max=0, min=0, replacement=False):
        integers = self.api.generate_integers(n, min, max, replacement=replacement)
        return integers

    @staticmethod
    def _get_max(items):
        return len(items) - 1

    def __init__(self, settings):
        self.api = RandomOrgClient(settings['api_key'])
