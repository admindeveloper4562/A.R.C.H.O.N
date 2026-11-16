import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend import CodeIndexError, RepositoryIndex


SOURCE_SHA = "a" * 40
BLOB_SHA = "b" * 40


class BackendCodeIndexTests(unittest.TestCase):
    def test_python_symbols_imports_tests_and_provenance_are_searchable(self):
        with tempfile.TemporaryDirectory() as directory:
            with RepositoryIndex(Path(directory) / "index.sqlite") as index:
                result = index.index_file(
                    "src/example.py",
                    "from jarvis_v2.backend import RepositoryIndex\n\nclass Demo:\n    pass\n\ndef test_demo():\n    return Demo()\n",
                    blob_sha=BLOB_SHA,
                    source_sha=SOURCE_SHA,
                )
                self.assertTrue(result["indexed"])
                hits = index.search("RepositoryIndex")
                self.assertEqual(hits[0]["path"], "src/example.py")
                self.assertEqual(hits[0]["blob_sha"], BLOB_SHA)
                symbols = index.symbols(path="src/example.py", source_sha=SOURCE_SHA)
                self.assertEqual({item["kind"] for item in symbols}, {"class", "import", "test"})

    def test_sensitive_sources_are_excluded_without_becoming_searchable(self):
        with tempfile.TemporaryDirectory() as directory:
            with RepositoryIndex(Path(directory) / "index.sqlite") as index:
                excluded = index.index_file(
                    ".env",
                    "API_KEY=do-not-index\n",
                    blob_sha=BLOB_SHA,
                    source_sha=SOURCE_SHA,
                )
                self.assertEqual(excluded["reason"], "sensitive_source")
                self.assertEqual(index.search("do-not-index"), [])
                self.assertEqual(index.symbols(), [])

    def test_reindex_replaces_old_blob_and_preserves_source_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            with RepositoryIndex(Path(directory) / "index.sqlite") as index:
                index.index_file("src/a.py", "def old_name(): pass\n", blob_sha=BLOB_SHA, source_sha=SOURCE_SHA)
                new_blob = "c" * 40
                index.index_file("src/a.py", "def new_name(): pass\n", blob_sha=new_blob, source_sha=SOURCE_SHA)
                self.assertEqual(index.search("old_name"), [])
                self.assertEqual(index.search("new_name")[0]["blob_sha"], new_blob)

    def test_invalid_provenance_and_python_fail_without_partial_index(self):
        with tempfile.TemporaryDirectory() as directory:
            with RepositoryIndex(Path(directory) / "index.sqlite") as index:
                with self.assertRaises(CodeIndexError):
                    index.index_file("../escape.py", "x", blob_sha=BLOB_SHA, source_sha=SOURCE_SHA)
                with self.assertRaises(CodeIndexError):
                    index.index_file("src/bad.py", "def broken(:\n", blob_sha=BLOB_SHA, source_sha=SOURCE_SHA)
                self.assertEqual(index.symbols(), [])


if __name__ == "__main__":
    unittest.main()
