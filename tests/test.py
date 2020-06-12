import unittest
import pathlib

from interutils.interactive import clear, pr, ask, banner, choose, pause, cyan, generic_menu_loop, get_date
from interutils.net import get_net, is_mac, ping
from interutils.fs import choose_file, count_lines, file_volume, human_bytes, is_image, is_package


class TestFS(unittest.TestCase):
    mockfile = pathlib.Path('tests/mockfile')

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

    # TODO
    # def test_is_image(self):
    #     pass


# TODO
# class TestNet(unittest.TestCase):
#     def test_get_net(self):
#         pass

if __name__ == '__main__':
    unittest.main()
