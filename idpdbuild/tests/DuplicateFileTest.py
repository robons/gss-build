import unittest
from pathlib import Path

from WafTestBase import WafTestBase


class DuplicateFileTaskTests(WafTestBase):

    def test_file_duplication(self):
        contents = "Hello, world."
        build_dir = self.build_root_path / "build"

        with open(self.build_root_path / "test.txt", "w+") as f:
            f.write(contents)

        self.set_script_and_configure(self.build_root_path, Path("DuplicateFileTest.wscript.py"))
        self.run_waf_script(self.build_root_path, ["build"])

        expected_file = build_dir / "test.txt.dupe"
        assert expected_file.exists()

        with open(expected_file, "r") as f:
            assert f.read() == contents


if __name__ == '__main__':
    unittest.main()

