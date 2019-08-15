# -------
# KeenTools for Blender unit-tests
# start it from commandline:
# blender -b -P /full_path_to/test_file.py
# -------
import unittest

import bpy
import sys
import os

# Import test functions used in unit-tests started from any location
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import test_utils
# import tests.test_utils as test_utils


from keentools_facebuilder.utils import manipulate, coords
from keentools_facebuilder.config import Config, get_main_settings


class FaceBuilderTest(unittest.TestCase):

    def _head_and_two_cameras(self):
        settings = get_main_settings()
        test_utils.create_head()
        headnum = settings.get_last_headnum()
        test_utils.create_empty_camera(headnum)

    def test_addon_on(self):
        test_utils.new_scene()
        settings = get_main_settings()
        self.assertEqual(0, len(settings.heads))

    def test_create_head_and_cameras(self):
        test_utils.new_scene()
        settings = get_main_settings()
        self.assertEqual(0, len(settings.heads))

        test_utils.create_head()
        self.assertEqual(1, len(settings.heads))

        headnum = settings.get_last_headnum()
        self.assertEqual(0, len(settings.heads[headnum].cameras))

        test_utils.create_empty_camera(headnum)
        test_utils.create_empty_camera(headnum)
        test_utils.create_empty_camera(headnum)
        self.assertEqual(3, len(settings.heads[headnum].cameras))

    def test_delete_cameras(self):
        # test_utils.new_scene()
        settings = get_main_settings()
        # self.assertEqual(0, len(settings.heads))
        test_utils.create_head()
        # self.assertEqual(1, len(settings.heads))
        headnum = settings.get_last_headnum()
        self.assertEqual(0, len(settings.heads[headnum].cameras))
        test_utils.create_empty_camera(headnum)
        test_utils.create_empty_camera(headnum)
        test_utils.create_empty_camera(headnum)
        test_utils.create_empty_camera(headnum)
        self.assertEqual(4, len(settings.heads[headnum].cameras))
        test_utils.delete_camera(headnum, 2)
        self.assertEqual(3, len(settings.heads[headnum].cameras))

    def test_move_pins(self):
        # Switch to PinMode
        settings = get_main_settings()
        test_utils.create_head()
        headnum = settings.get_last_headnum()
        test_utils.create_empty_camera(headnum)
        test_utils.create_empty_camera(headnum)
        camnum = settings.get_last_camnum(headnum)
        test_utils.select_camera(headnum, camnum)
        print("camera selected")

        area = manipulate.get_area()
        region_3d = area.spaces[0].region_3d

        fake_context = lambda: None
        fake_context.area = area
        fake_context.space_data = lambda: None
        fake_context.space_data.region_3d = region_3d
        fake_context.scene = bpy.context.scene

        brect = tuple(coords.get_camera_border(bpy.context))
        arect = (396.5, -261.9, 1189.5, 1147.9)

        test_utils.move_pin(793, 421, 651, 425, arect, brect)
        test_utils.move_pin(732, 478, 826, 510, arect, brect)
        test_utils.move_pin(542, 549, 639, 527, arect, brect)
        test_utils.move_pin(912, 412, 911, 388, arect, brect)

        # Coloring wireframe
        op = getattr(
            bpy.ops.object, Config.fb_main_wireframe_color_callname)
        op('EXEC_DEFAULT', action='wireframe_green')


    def test_duplicate_and_reconstruct(self):
        settings = get_main_settings()
        test_utils.create_head()
        headnum = settings.get_last_headnum()
        test_utils.deselect_all()
        headobj = test_utils.select_by_headnum(headnum)
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
            TRANSFORM_OT_translate={"value": (-3.0, 0, 0)})

        op = getattr(
            bpy.ops.object, Config.fb_actor_operator_callname)
        op('EXEC_DEFAULT', action='reconstruct_by_head', headnum=-1, camnum=-1)


if __name__ == "__main__":
    # unittest.main()  # -- Doesn't work with Blender, so we use Suite
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FaceBuilderTest)
    unittest.TextTestRunner().run(suite)
