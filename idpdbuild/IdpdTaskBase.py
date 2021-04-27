from pathlib import Path
from typing import List

from waflib.Build import BuildContext
from waflib.Node import Nod3
from waflib.Task import Task


class IdpdTaskBase(Task):
    inputs: List[Nod3]
    outputs: List[Nod3]

    def exec_commands(self, commands: List[str]) -> int:
        for command in commands:
            response = self.exec_command(command)
            if response != 0:
                return response

        return 0

    def get_path_relative_to_build_path(self, node: Nod3) -> str:
        build_context: BuildContext = self.generator.bld
        return node.path_from(build_context.path)

    def get_commands_copy_dependent_files_to(self, to_dir: str) -> List[str]:
        all_dependent_nodes = self.inputs + self.dep_nodes

        commands = []

        def ensure_parent_dir_exists(file: Nod3):
            destination_folder = file.parent
            command = f"mkdir -p {destination_folder}"
            if command not in commands:
                commands.append(command)

        for f in all_dependent_nodes:
            destination_file = Path(to_dir) / self.get_path_relative_to_build_path(f)
            ensure_parent_dir_exists(destination_file)
            commands.append(f"cp '{f.abspath()}' '{destination_file}'")

        # ensure build folder structure exist for output files.
        for f in self.outputs:
            destination_file = Path(to_dir) / self.get_path_relative_to_build_path(f)
            ensure_parent_dir_exists(destination_file)

        return commands

    def get_commands_copy_output_files_from(self, from_dir: str) -> List[str]:
        return [f"cp '{Path(from_dir) / self.get_path_relative_to_build_path(f)}' '{f.abspath()}'"
                for f in self.outputs]
