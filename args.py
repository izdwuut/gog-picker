from configparser import RawConfigParser
import sys


class Args:
    url = None
    replacement = None
    all = None
    number = None
    verbose = None
    links = None

    @classmethod
    def from_namespace(cls, namespace):
        return Args._set_args(cls(), namespace)

    @classmethod
    def from_config(cls, config):
        args = cls()
        args.replacement = cls._get_val(config, 'replacement', bool)
        args.all = cls._get_val(config, 'all', bool)
        args.number = cls._get_val(config, 'number', int)
        args.verbose = cls._get_val(config, 'verbose', bool)
        args.links = cls._get_val(config, 'links', bool)
        return args

    def update(self, args):
        Args._set_args(args, self)

    @staticmethod
    def _set_args(from_, to):
        for attr, value in vars(from_).items():
            if value is not None:
                setattr(to, attr, value)
        return to

    @staticmethod
    def _get_val(config, arg, type_):
        if type_ is bool:
            getter = 'getboolean'
        if type_ is int:
            getter = 'getint'
        if not config.get(arg):
            return None
        try:
            val = getattr(config, getter)(arg)
        except ValueError:
            print("Wrong argument's value: args.{}.".format(arg))
            sys.exit(2)
        return val
