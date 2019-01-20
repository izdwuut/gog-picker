class Args:
    url = None
    replacement = False
    all = False
    number = 1
    verbose = False

    @classmethod
    def from_namespace(cls, namespace):
        args = cls()
        for attr, value in vars(namespace).items():
            setattr(args, attr, value)
        return args
