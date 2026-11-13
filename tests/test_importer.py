import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from tools.import_legacy import prepare_manifest

class ImporterTests(unittest.TestCase):
    def test_fixture_import_dry_run_then_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);src=base/"old";dest=base/"new"
            src.mkdir();dest.mkdir()
            def git(*a):return subprocess.run(["git","-C",str(src),*a],capture_output=True,text=True,check=True).stdout.strip()
            git("init","-b","develop")
            git("config","user.name","Test")
            git("config","user.email","t@example.test")
            (src/"source.py").write_text("def hello(): return 1\n")
            git("add","source.py");git("commit","-m","initial")
            git("remote","add","origin","https://github.com/admindeveloper4562/personal-jarvis.git")
            git("update-ref","refs/remotes/origin/develop",git("rev-parse","HEAD"))
            manifest={"schema":"jarvis-v2.legacy-import/1","entries":[{"area":"core","ref":"develop","source":"source.py","target":"migration/imported/core/source.py"}]}
            dry=prepare_manifest(src,dest,manifest)
            self.assertTrue(dry["dry_run"])
            self.assertFalse((dest/"migration/imported/core/source.py").exists())
            applied=prepare_manifest(src,dest,manifest,apply=True)
            self.assertEqual(applied["count"],1)
            self.assertIn("hello",(dest/"migration/imported/core/source.py").read_text())
            with self.assertRaises(FileExistsError):prepare_manifest(src,dest,manifest,apply=True)
    def test_unsafe_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);repo=p/"old";dest=p/"new";repo.mkdir();dest.mkdir()
            def git(*a):return subprocess.run(["git","-C",str(repo),*a],capture_output=True,text=True,check=True).stdout.strip()
            git("init","-b","develop");git("config","user.name","Test");git("config","user.email","t@example.test")
            (repo/"x").write_text("x");git("add","x");git("commit","-m","init")
            git("remote","add","origin","https://github.com/admindeveloper4562/personal-jarvis.git")
            git("update-ref","refs/remotes/origin/develop",git("rev-parse","HEAD"))
            manifest={"schema":"jarvis-v2.legacy-import/1","entries":[{"area":"core","ref":"develop","source":"x","target":"../other"}]}
            with self.assertRaises(ValueError):prepare_manifest(repo,dest,manifest)
if __name__=="__main__":unittest.main()
