from waflib.Node import Nod3
from waflib.Build import BuildContext
from waflib import TaskGen
from typing import List, Any
from tempfile import TemporaryDirectory

from idpdbuild import TaskColours
from idpdbuild.IdpdTaskBase import IdpdTaskBase
from .CsvWHelpers import get_dependent_files_for_metadata


@TaskGen.after("CsvLintTask")
class Csv2RdfTask(IdpdTaskBase):

    color = TaskColours.GREEN

    @staticmethod
    def register_tasks(bld: BuildContext, inputs: List[Nod3], group="CSV2RDF"):
        if group not in bld.groups:
            bld.add_group(group)

        for f in inputs:
            task = Csv2RdfTask(Csv2RdfTask, "csv2rdf", bld.env.derive())
            task.set_inputs(f)
            task.set_outputs(f.change_ext(".ttl"))
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
        file_out = self.outputs[0]
        file_in.h_file()
        with TemporaryDirectory() as temp_dir:
            commands = self.get_commands_copy_dependent_files_to(temp_dir)
            commands.append(
                f"docker run --rm -v '{temp_dir}':/workspace -w /workspace gsscogs/csv2rdf csv2rdf " +
                f"-u '{self.get_path_relative_to_build_path(file_in)}' " +
                f"-o '{self.get_path_relative_to_build_path(file_out)}'"
            )
            commands += self.get_commands_copy_output_files_from(temp_dir)

            return self.exec_commands(commands)

