# ##### BEGIN GPL LICENSE BLOCK #####
# KeenTools for blender is a blender addon for using KeenTools in Blender.
# Copyright (C) 2019  KeenTools

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####


import bpy
import json
import time
from . config import get_main_settings


class FBDebug:
    """ Debug purpose object """
    event_number = 0
    event_queue = []
    lastx = 0
    lasty = 0
    timer = time.clock()

    SNAPSHOTS_FILENAME = 'facebuilder_debug_snapshots'
    EVENTS_FILENAME = 'facebuilder_debug_events'

    snapshots_file = None
    events_file = None

    # Log Activity flag
    active = False

    @classmethod
    def set_active(cls, flag=True):
        print("IN_SET:", flag)
        cls.active = flag
        print("AFTER_SET:", cls.active)

    @classmethod
    def inc_event_number(cls):
        cls.event_number += 1

    @classmethod
    def get_event_number(cls):
        return cls.event_number

    @classmethod
    def get_timer(cls):
        now = time.clock()
        old = cls.timer
        cls.timer = now
        return (now - old)

    @classmethod
    def add_event_to_queue(cls, eventname, p, b=(-1, -1, -1, -1, -1, -1, -1)):
        if not cls.active:
            return
        cls.inc_event_number()
        cls.event_queue.append((
            cls.get_event_number(), eventname, p[0], p[1],
            p[0] - cls.lastx, p[1] - cls.lasty,
            b[0], b[1], b[2], b[3], b[4], b[5], b[6],
            cls.get_timer()
        ))
        cls.lastx = p[0]
        cls.lasty = p[1]

    @classmethod
    def format_event_output(cls, ev):
        return "\n[{0[0]}] {0[1]} time:{0[13]:.4f}s\n x:{0[2]}  y:{0[3]} dx:{0[4]} dy:{0[5]}\n a:({0[6]},{0[7]}) ({0[8]},{0[9]}) z:{0[10]} off:({0[11]}, {0[12]})".format(
            ev)

    @classmethod
    def clear_event_queue(cls):
        if not cls.active:
            return
        cls.make_snapshot()
        fe = cls.get_events_file()
        for ev in cls.event_queue:
            res = cls.format_event_output(ev)
            fe.write(res)
        cls.event_queue = []

    @classmethod
    def output_event_queue(cls):
        if not cls.active:
            return
        # Need output all in Text Editor
        print("=== QUEUE ===")
        for ev in cls.event_queue:
            res = cls.format_event_output(ev)
            print(res)

    @classmethod
    def make_snapshot(cls):
        if not cls.active:
            return
        cls.inc_event_number()
        fs = cls.get_snapshots_file()
        fs.write("\n\n[{}]\n".format(cls.get_event_number()))
        res = cls.get_settings()
        fs.write("{}\n".format(json.dumps(res)))

    @classmethod
    def get_settings(cls):
        settings = get_main_settings()
        h_arr = []
        for h in settings.heads:
            c_arr = []
            for c in h.cameras:
                c_arr.append({
                    'model_mat': c.model_mat,
                    'frame_width': settings.frame_width,
                    'frame_height': settings.frame_height
                })
            head_info = {
                'serial': h.serial_str
            }
            h_arr.append(head_info)
        res = {
            'current_headnum': settings.current_headnum,
            'current_camnum': settings.current_camnum,
            'heads': h_arr,
            'sensor_width': settings.sensor_width,
            'focal': settings.focal
        }
        return res

    @classmethod
    def get_snapshots_file(cls):
        if cls.snapshots_file is None:
            n = bpy.data.texts.find(cls.SNAPSHOTS_FILENAME)
            if n >= 0:
                cls.snapshots_file = bpy.data.texts[n]
            else:
                cls.snapshots_file = bpy.data.texts.new(cls.SNAPSHOTS_FILENAME)
        return cls.snapshots_file

    @classmethod
    def get_events_file(cls):
        if cls.events_file is None:
            n = bpy.data.texts.find(cls.EVENTS_FILENAME)
            if n >= 0:
                cls.events_file = bpy.data.texts[n]
            else:
                cls.events_file = bpy.data.texts.new(cls.EVENTS_FILENAME)
        return cls.events_file
