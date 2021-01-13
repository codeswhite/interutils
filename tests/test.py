import unittest
import unittest.mock as mock
from pathlib import Path
import shutil
import pathlib
import tempfile
import sys
from io import BytesIO, StringIO

from interutils import *


# Test Helper Objects
class Base(unittest.TestCase):
    @staticmethod
    def mock_property(name):
        return mock.patch(name, new_callable=mock.PropertyMock)

    def assert_called_once(self, mock_method):
        self.assertEqual(mock_method.call_count, 1)


class BaseMockDir(Base):
    @property
    def dir_count(self):
        return len(tuple(self.test_dir.iterdir()))

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

class BaseStdout(Base):
    def setUp(self):
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = sys.__stdout__


class TestInteractive(BaseStdout):
    def setUp(self):
        BaseStdout.setUp(self)

    def test_pr(self):
        text = 'loremipsum'
        pr(text)
        self.assertIn(text, sys.stdout.getvalue())
    
    @mock.patch('builtins.input', side_effect=('', 'asdf', '2'))
    def test_choose_default(self, _):
        self.assertEqual(choose(), 0)
        self.assertEqual(choose(), -1)
        self.assertEqual(choose(), 1)


    @mock.patch('builtins.input')
    def test_ask(self, mock_input):
        mock_input.side_effect = ('foobar', '')
        
        res = ask('loermipsum')
        self.assertEqual(res, 'foobar')
        self.assertIn('loermipsum', sys.stdout.getvalue())

        res = ask('doooo')
        self.assertIsNone(res)
        self.assertIn('doooo', sys.stdout.getvalue())


class TestFS(unittest.TestCase):
    def setUp(self):
        import random
        import string
        self.mockfile = pathlib.Path(
            'mockfile' + random.choice(string.digits) * 10)
        self.mockfile.write_text('a\nb\nc', encoding='utf-8')
        self.emptyfile = pathlib.Path(
            'emptyfile' + random.choice(string.digits) * 10)
        self.emptyfile.touch()

    def tearDown(self):
        import os
        os.remove(self.mockfile)
        os.remove(self.emptyfile)

    def test_count_lines(self):
        self.assertEqual(count_lines(self.emptyfile), 0)
        self.assertEqual(count_lines(self.mockfile), 3)

    def test_file_volume(self):
        fv = file_volume(self.mockfile)
        self.assertEqual(fv[0], 5)
        self.assertEqual(fv[1], 3)

    def test_human_bytes(self):
        for i in range(5):
            self.assertEqual(human_bytes(1024**i), '1' +
                             ('', 'KB', 'MB', 'GB', 'TB')[i])

    def test_is_package(self):
        self.assertIsNone(is_package(
            'rundom-unexisting-packagename-64198938249071658123'))

# TODO
# class TestNet(unittest.TestCase):
#     def test_get_net(self):
#         pass


if __name__ == '__main__':
    unittest.main()
