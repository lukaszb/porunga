import os


joinpath = lambda *p: os.path.join(*p)
abspath = lambda *p: os.path.abspath(joinpath(*p))

