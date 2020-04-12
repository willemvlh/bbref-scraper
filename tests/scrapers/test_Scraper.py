from pathlib import Path


def get_resource(fn):
    return str(Path(__file__).parent.parent.joinpath("resources").joinpath(fn).absolute())
