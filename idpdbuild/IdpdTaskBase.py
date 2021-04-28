import inspect
import sys
from pathlib import Path
from typing import List, ClassVar

from waflib.Build import BuildContext
from waflib.Node import Nod3
from waflib.Task import Task
import hashlib


class IdpdTaskBase(Task):
    inputs: List[Nod3]
    outputs: List[Nod3]

    name: str
    classHash: bytes

    def __init__(self, c: ClassVar,name: str, env):
        Task.__init__(self, env=env)
        self.name = name
        self.classHash = hashlib.md5(inspect.getsource(c).encode()).digest()
        self.vars.append(self.classHash)

    def exec_commands(self, commands: List[str]) -> int:
        for command in commands:
            response = self.exec_command(command)
            if response != 0:
                print(f"({self.name}) ERROR: Failed when running command \"{command}\"", file=sys.stderr)
                return response

        return 0

    def get_path_relative_to_build_path(self, node: Nod3) -> str:
        build_context: BuildContext = self.generator.bld
        return node.path_from(build_context.path)

    def get_commands_copy_dependent_files_to(self, to_dir: str) -> List[str]:
        all_dependent_nodes = self.inputs + self.scan()[0]

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

    def keyword(self):
        """
        Overrides keyword method used to print build information to the console
        > [3/4] csv2rdf codelists/sector.csv-metadata.json
        """
        return self.name
