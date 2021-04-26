import unittest
from pathlib import Path
from typing import List
import sys
import os
import inspect
from waflib import Scripting, Build
from tempfile import TemporaryDirectory

wafdir = Path(os.path.abspath(inspect.getfile(inspect.getmodule(Build.BuildContext)))).parent
VERSION = "2.0.22"


class WafTestBase(unittest.TestCase):
    tmp_dir: TemporaryDirectory = None
    build_root_path: Path = None

    def setUp(self) -> None:
        self.tmp_dir = TemporaryDirectory()
        self.build_root_path = Path(self.tmp_dir.name)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()
        self.tmp_dir = None
        self.build_root_path = None

    def set_script_and_configure(self, build_dir: Path, script_path: Path):
        with open(script_path) as f:
            script_contents = f.read()

        self.set_waf_script(build_dir, script_contents)
        self.run_waf_script(build_dir, ["configure"])

    def set_waf_script(self, build_dir: Path, script: str):
        waf_file_path = Path(build_dir) / "wscript"
        with open(waf_file_path, "w+") as f:
            f.write(script)

    def run_waf_script(self, build_dir: Path, args: List[str]):
        # First command is ignored since it's probably the python script's path.
        sys.argv = ["waf-light"] + args
        Scripting.waf_entry_point(str(build_dir), VERSION, wafdir)


