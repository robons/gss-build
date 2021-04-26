from waflib.Task import Task
from waflib.Node import Nod3
from waflib.Build import BuildContext


class DuplicateFileTask(Task):
    run_str = "cp ${SRC} ${TGT}"

    def __init__(self, bld: BuildContext, input_file: Nod3):
        Task.__init__(self, env=bld.env.derive())
        output_file: Nod3 = bld.path.find_or_declare(input_file.name + ".dupe")
        self.set_inputs(input_file)
        self.set_outputs(output_file)
