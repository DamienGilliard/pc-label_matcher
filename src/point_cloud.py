import os

import numpy as np
import numpy.lib.recfunctions as rfn
from plyfile import PlyElement, PlyData

import utils

class PointCloud:
    """
    This class represents a point cloud with its associated data.
    """
    
    def __init__(self, pc, pc_label=None, type_str="LAS"):
        self.pc = pc
        self.type_str = type_str
        self.localisation = self.get_bbox_2d_center()
        self.label = pc_label
        


    def get_bbox_2d_center(self):
        if self.type_str == "PLY":
            points = self.pc['vertex']
            xs = points['x']
            ys = points['y']
            zs = points['z']
            mean_x = (min(xs) + max(xs)) / 2
            mean_y = (min(ys) + max(ys)) / 2
            mean_z = (min(zs) + max(zs)) / 2
            if mean_x < 180 and mean_y < 90:
                print("Point cloud seems to be in WGS84 coordinates, converting to LV95.")
                mean_x, mean_y, mean_z = utils.convert_wgs84_to_lv95(mean_x, mean_y, mean_z)
            return (mean_y, mean_x)
        elif self.type_str == "LAS":
            mean = (self.pc.header.mins + self.pc.header.maxs) / 2
            if mean[0] < 180 and mean[1] < 90:
                print("Point cloud seems to be in WGS84 coordinates, converting to LV95.")
                mean = utils.convert_wgs84_to_lv95(mean[0], mean[1], mean[2])
        return (mean[1], mean[0])
    
    def apply_label(self, pc_label):
        if self.type_str == "LAS":
            self.pc.classification[:] = int(pc_label.label)
        elif self.type_str == "PLY":
            vertex = self.pc['vertex']
            data = vertex.data

            if 'Classification' not in data.dtype.names:
                data = rfn.append_fields(
                            data,
                            'Classification',
                            np.full(data.shape, int(pc_label.label), dtype=np.uint8),
                            usemask=False,
                            dtypes=[np.uint8]
                        )
            else:
                data['Classification'] = int(pc_label.label)
            vertex_element = PlyElement.describe(data, 'vertex')
            self.pc = PlyData([vertex_element], text=self.pc.text)
            
    def store_pc(self, folder_path, filename=None):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if self.type_str == "LAS":
            filename = f"pc_with_label_at_{self.localisation[0]}_{self.localisation[1]}.las"
            output_path = os.path.join(folder_path, filename)
            self.pc.write(output_path)
        elif self.type_str == "PLY":
            filename = f"pc_with_label_at_{self.localisation[0]}_{self.localisation[1]}.ply"
            output_path = os.path.join(folder_path, filename)
            self.pc.write(output_path)