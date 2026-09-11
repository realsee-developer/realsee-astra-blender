"""Tests for the preparation helper, without Blender or private scene inputs."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "project", Path(__file__).resolve().parents[1] / "tools/project.py")
project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)


class InventoryTests(unittest.TestCase):
    def test_nested_files_and_formats(self):
        with tempfile.TemporaryDirectory() as temp:
            data = Path(temp)
            (data / "model").mkdir()
            (data / "model/scan.OBJ").write_bytes(b"mesh")
            (data / "photo.jpg").write_bytes(b"image")
            (data / ".DS_Store").write_bytes(b"ignored")
            (data / ".private").mkdir()
            (data / ".private/key.txt").write_bytes(b"ignored")
            result = project.inventory(data)
            self.assertEqual(result["file_count"], 2)
            self.assertEqual(result["total_bytes"], 9)
            self.assertEqual(result["formats"], {".jpg": 1, ".obj": 1})
            self.assertEqual(result["files"][0]["path"], "model/scan.OBJ")

    def test_missing_folder_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(NotADirectoryError):
                project.inventory(Path(temp) / "missing")

    def test_missing_blender_is_an_error(self):
        with self.assertRaises(FileNotFoundError):
            project.blender_executable("definitely-no-such-blender-executable")


if __name__ == "__main__":
    unittest.main()
