import unittest
import pathlib

from interutils import *


class TestFS(unittest.TestCase):
    def setUp(self):
        import random
        import string
        self.mockfile = pathlib.Path(
            'mockfile' + random.choice(string.digits) * 10)
        self.mockfile.write_text('a\nb\nc', encoding='utf-8')

    def tearDown(self):
        import os
        os.remove(self.mockfile)

    def test_count_lines(self):
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
        # TODO find a way to actuall check
    # TODO
    # def test_is_image(self):
    #     pass


# TODO
# class TestNet(unittest.TestCase):
#     def test_get_net(self):
#         pass

if __name__ == '__main__':
    unittest.main()
