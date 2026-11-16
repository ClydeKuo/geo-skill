import os
import shutil
import subprocess
import tempfile
import unittest

from helpers import HERE

SKILL = os.path.dirname(HERE)
SCRIPT = os.path.join(SKILL, "install.sh")


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.home)
        self.project = os.path.join(self.tmp, "proj")
        os.makedirs(self.project)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_install(self, *args):
        env = dict(os.environ, HOME=self.home)
        return subprocess.run(["bash", SCRIPT] + list(args), capture_output=True, text=True, env=env, timeout=30)

    def assertLinksToSkill(self, path):
        self.assertTrue(os.path.islink(path), path)
        self.assertEqual(os.path.realpath(path), os.path.realpath(SKILL))

    def test_project_install_relative_links(self):
        r = self.run_install("--project", self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        for d in (".claude/skills/geo-audit", ".agents/skills/geo-audit"):
            p = os.path.join(self.project, d)
            self.assertLinksToSkill(p)
            self.assertFalse(os.path.isabs(os.readlink(p)))
        self.assertFalse(os.path.exists(os.path.join(self.project, ".cursor")))

    def test_user_install(self):
        r = self.run_install("--user")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLinksToSkill(os.path.join(self.home, ".claude/skills/geo-audit"))
        self.assertLinksToSkill(os.path.join(self.home, ".agents/skills/geo-audit"))

    def test_idempotent_skip(self):
        self.run_install("--project", self.project)
        r = self.run_install("--project", self.project)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("skip", r.stdout)

    def test_conflict_not_overwritten(self):
        conflict = os.path.join(self.project, ".agents/skills/geo-audit")
        os.makedirs(conflict)
        open(os.path.join(conflict, "keep.txt"), "w").close()
        r = self.run_install("--project", self.project)
        self.assertEqual(r.returncode, 1)
        self.assertIn("already exists", r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(conflict, "keep.txt")))
        self.assertLinksToSkill(os.path.join(self.project, ".claude/skills/geo-audit"))

    def test_path_with_space(self):
        proj = os.path.join(self.tmp, "my project")
        os.makedirs(proj)
        r = self.run_install("--project", proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLinksToSkill(os.path.join(proj, ".claude/skills/geo-audit"))

    def test_cursor_tool(self):
        r = self.run_install("--project", self.project, "--tools", "cursor")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLinksToSkill(os.path.join(self.project, ".cursor/skills/geo-audit"))
        self.assertFalse(os.path.exists(os.path.join(self.project, ".claude")))


if __name__ == "__main__":
    unittest.main()
