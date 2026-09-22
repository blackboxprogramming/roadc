"""Public CLI regressions, also runnable with the standard-library test runner."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / 'roadc.py'


class CheckFailureTests(unittest.TestCase):
    def invoke(self, program, command='check'):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'program.road'
            source.write_text(program, encoding='utf-8')
            return subprocess.run(
                [sys.executable, str(CLI), command, str(source)],
                capture_output=True, text=True, timeout=2,
            )

    def test_unfinished_statements_fail_without_hanging(self):
        for program in (
            'type Device:\n    name: str\n',
            'match value:\n    let x = 1\n',
            'fun task():\n    spawn worker()\n',
            'export type Device:\n    name: str\n',
        ):
            with self.subTest(program=program):
                result = self.invoke(program)
                self.assertEqual(result.returncode, 1)
                self.assertIn('Unsupported statement', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertNotIn('Syntax OK', result.stdout)

    def test_malformed_number_has_clean_diagnostic(self):
        result = self.invoke('let x = 1.2.3\n')
        self.assertEqual(result.returncode, 1)
        self.assertIn('program.road:', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertNotIn('Syntax OK', result.stdout)

    def test_supported_programs_are_checked_without_execution(self):
        for program in (
            '', '\n\n# Only a comment\n',
            'print("MUST NOT EXECUTE")\nlet x = 1 / 0\n',
            'fun task():\n    while true:\n        print("MUST NOT EXECUTE")\n',
        ):
            with self.subTest(program=program):
                result = self.invoke(program)
                self.assertEqual(result.returncode, 0)
                self.assertIn('Syntax OK', result.stdout)
                self.assertNotIn('MUST NOT EXECUTE', result.stdout)
                self.assertEqual(result.stderr, '')

    def test_existing_run_and_parse_commands_still_work(self):
        result = self.invoke('print("hello")\n', command='run')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, 'hello\n')
        result = self.invoke('print("hello")\n', command='parse')
        self.assertEqual(result.returncode, 0)
        self.assertIn('ExpressionStatement', result.stdout)


if __name__ == '__main__':
    unittest.main()
