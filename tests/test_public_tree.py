"""LFS checks work with both fetched binaries and pointer-only CI checkouts."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "public_tree", Path(__file__).resolve().parents[1] / "tools/check_public_tree.py")
public_tree = importlib.util.module_from_spec(spec)
spec.loader.exec_module(public_tree)


def pointer_for(content):
    return ("version https://git-lfs.github.com/spec/v1\n"
            f"oid sha256:{hashlib.sha256(content).hexdigest()}\n"
            f"size {len(content)}\n").encode()


class LfsTests(unittest.TestCase):
    def test_binary_and_pointer_checkout(self):
        content = b"synthetic scene bytes"
        pointer = pointer_for(content)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scene.blend"
            for working in (content, pointer):
                path.write_bytes(working)
                public_tree.check_lfs_content(path, pointer)

    def test_corruption_and_raw_git_blob_are_rejected(self):
        content = b"scene"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scene.blend"
            path.write_bytes(b"Scene")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                public_tree.check_lfs_content(path, pointer_for(content))
            with self.assertRaisesRegex(ValueError, "index must contain"):
                public_tree.check_lfs_content(path, content)

    def test_published_source_requires_manifest_identity(self):
        content = b"authorized original source"
        name = "data/panorama/1.jpg"
        entries = {name: {"sha256": hashlib.sha256(content).hexdigest(),
                          "bytes": len(content)}}
        public_tree.check_data_pointer(name, pointer_for(content), entries)
        with self.assertRaisesRegex(ValueError, "not in the published"):
            public_tree.check_data_pointer("data/private.jpg", pointer_for(content), entries)
        with self.assertRaisesRegex(ValueError, "differs from"):
            public_tree.check_data_pointer(name, pointer_for(b"other source"), entries)

    def test_mismatched_pointer_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scene.blend"
            path.write_bytes(pointer_for(b"different"))
            with self.assertRaisesRegex(ValueError, "pointer differs"):
                public_tree.check_lfs_content(path, pointer_for(b"expected"))


if __name__ == "__main__":
    unittest.main()
