from waflib.Node import Nod3
from waflib import TaskGen
from typing import List, Any
from tempfile import TemporaryDirectory

from idpdbuild.IdpdTaskBase import IdpdTaskBase


class Csv2RdfTask(IdpdTaskBase):
    @staticmethod
    def register_task_with_file_extensions():
        @TaskGen.extension(".csv-metadata.json")
        def register_task_for_file(task_gen_ctx: TaskGen.task_gen, file: Nod3):
            output_file = file.change_ext(".ttl")
            task_gen_ctx.create_task(Csv2RdfTask.__name__, file, output_file)

    def scan(self) -> (List[Nod3], List[Any]):
        """
        Find implicit dependencies for this task.
        """
        implicit_dependencies = []
        for input_file in self.inputs:
            csvw_schema = input_file.read_json()
            if "url" in csvw_schema:
                implicit_dependencies.append(csvw_schema["url"])
            elif "tables" in csvw_schema:
                for table in csvw_schema["tables"]:
                    if "url" in table:
                        implicit_dependencies.append(table["url"])
        # todo: Probably want to pull foreign key related table URLs out here too.

        self.dep_nodes += [input_file.parent.find_node(d) for d in implicit_dependencies]
        return self.dep_nodes, []

    def run(self) -> int:
        file_in = self.inputs[0]
        file_out = self.outputs[0]
        with TemporaryDirectory() as temp_dir:
            commands = self.get_commands_copy_dependent_files_to(temp_dir)
            commands += []
            commands.append(
                f"docker run --rm -v '{temp_dir}':/workspace -w /workspace gsscogs/csv2rdf csv2rdf " +
                f"-u '{self.get_path_relative_to_build_path(file_in)}' " +
                f"-o '{self.get_path_relative_to_build_path(file_out)}'"
            )
            commands += self.get_commands_copy_output_files_from(temp_dir)

            return self.exec_commands(commands)
