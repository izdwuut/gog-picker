class Args:
    url = None
    replacement = False
    all = False
    number = 1
    verbose = False

    @classmethod
    def from_dict(cls, dict_):
        args = cls()
        for attr, value in dict_.items():
            setattr(args, attr, value)
        return args