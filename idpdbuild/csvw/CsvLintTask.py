from waflib.Node import Nod3
from waflib.Build import BuildContext
from typing import List, Any
from tempfile import TemporaryDirectory
from waflib import TaskGen

from idpdbuild.IdpdTaskBase import IdpdTaskBase
from .CsvWHelpers import get_dependent_files_for_metadata
from .Csv2RdfTask import Csv2RdfTask


@TaskGen.before(Csv2RdfTask.__name__)
class CsvLintTask(IdpdTaskBase):
    @staticmethod
    def register_tasks(bld: BuildContext, inputs: List[Nod3], group="csv-lint"):
        if group not in bld.groups:
            bld.add_group(group)

        for f in inputs:
            task = CsvLintTask(CsvLintTask, "csv-lint", bld.env.derive())
            task.set_inputs(f)
            bld.add_to_group(task, group=group)

    def scan(self) -> (List[Nod3], List[Any]):
        """
        Find implicit dependencies for this task.
        """
        for input_file in self.inputs:
            self.dep_nodes += get_dependent_files_for_metadata(input_file)

        return self.dep_nodes, []

    def run(self) -> int:
        file_in = self.inputs[0]
        with TemporaryDirectory() as temp_dir:
            commands = self.get_commands_copy_dependent_files_to(temp_dir)
            commands.append(
                f"docker run --rm -v '{temp_dir}':/workspace -w /workspace gsscogs/csvlint csvlint " +
                f"-s '{self.get_path_relative_to_build_path(file_in)}' "
            )
            commands += self.get_commands_copy_output_files_from(temp_dir)

            return self.exec_commands(commands)
