import unittest
import sys
import types

if 'tkinter' not in sys.modules:
    tkinter_module = types.ModuleType('tkinter')
    ttk_module = types.ModuleType('tkinter.ttk')
    filedialog_module = types.ModuleType('tkinter.filedialog')
    messagebox_module = types.ModuleType('tkinter.messagebox')
    tkinter_module.ttk = ttk_module
    tkinter_module.filedialog = filedialog_module
    tkinter_module.messagebox = messagebox_module
    sys.modules['tkinter'] = tkinter_module
    sys.modules['tkinter.ttk'] = ttk_module
    sys.modules['tkinter.filedialog'] = filedialog_module
    sys.modules['tkinter.messagebox'] = messagebox_module

from apriltag_generator import AprilTagGenerator


class AprilTagGeneratorTests(unittest.TestCase):
    def test_generate_tag_honors_non_divisible_dimensions(self):
        img = AprilTagGenerator.generate_tag(0, size=123, style='rectangular')
        self.assertEqual(img.size, (123, 123))

    def test_generate_tag_has_white_outer_border(self):
        img = AprilTagGenerator.generate_tag(0, size=120, style='rectangular')
        self.assertEqual(img.getpixel((0, 0)), 255)
        self.assertEqual(img.getpixel((119, 0)), 255)
        self.assertEqual(img.getpixel((0, 119)), 255)
        self.assertEqual(img.getpixel((119, 119)), 255)


if __name__ == '__main__':
    unittest.main()
