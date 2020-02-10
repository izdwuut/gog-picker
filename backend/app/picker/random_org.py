from rdoclient_py3 import RandomOrgClient


class RandomOrg:
    def items(self, items, n=1, replacement=False):
        max = RandomOrg._get_max(items)
        integers = self._get_integers(n, max, replacement=replacement)
        return [items[i] for i in integers]

    def _get_integers(self, n=1, max=0, min=0, replacement=False):
        integers = self.api.generate_integers(n, min, max, replacement=replacement)
        return integers

    @staticmethod
    def _get_max(items):
        return len(items) - 1

    def __init__(self, api_key):
        self.api = RandomOrgClient(api_key)
