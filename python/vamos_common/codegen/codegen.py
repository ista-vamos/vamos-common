from os import mkdir
from os.path import join as pathjoin, abspath
from shutil import rmtree, copy as shutilcopy

from sys import stderr

from ..spec.ir.type import Type, BoolType, IntType, UIntType

class CodeGen:
    def __init__(self, args, ctx):
        self.args = args
        self._generated_files = []
        self.out_dir = abspath(args.out_dir)
        self.templates_path = None
        self.ctx = ctx

        try:
            mkdir(self.out_dir)
        except OSError:
            print("The output dir exists, overwriting its contents", file=stderr)
            rmtree(self.out_dir)
            mkdir(self.out_dir)

        if args.debug:
            mkdir(f"{self.out_dir}/dbg")

    def copy_file(self, name):
        path = pathjoin(self.templates_path, name)
        shutilcopy(path, self.out_dir)

    def new_file(self, name):
        if name in self.args.overwrite_default:
            filename = "/dev/null"
        else:
            filename = pathjoin(self.out_dir, name)
            assert filename not in self._generated_files, (filename, self._generated_files)
            self._generated_files.append(filename)
        return open(filename, "w")

    def new_dbg_file(self, name):
        filename = pathjoin(self.out_dir, "dbg/", name)
        return open(filename, "w")

    def gen_config(self, infile, outfile, values):
        if outfile in self.args.overwrite_default:
            return
        inpath = pathjoin(self.templates_path, infile)
        outpath = pathjoin(self.out_dir, outfile)
        with open(inpath, "r") as infl:
            with open(outpath, "w") as outfl:
                for line in infl:
                    if "@" in line:
                        for v, s in values.items():
                            assert v.startswith("@"), v
                            assert v.endswith("@"), v
                            line = line.replace(v, s)
                    outfl.write(line)

    def input_file(self, stream, name):
        inpath = pathjoin(self.templates_path, name)
        with open(inpath, "r") as infl:
            write = stream.write
            for line in infl:
                write(line)
