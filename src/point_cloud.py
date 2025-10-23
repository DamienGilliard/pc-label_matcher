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
        self.label = pc_label
        self.scalar_field_name = None
        if self.scalar_field_name:
            if self.type_str == "LAS":
                self.n_clusters = len(np.unique(self.pc.classification))
            elif self.type_str == "PLY":
                self.n_clusters = len(np.unique(self.pc['vertex'][self.scalar_field_name]))
        else:
            self.n_clusters = 1
        if self.n_clusters == 1:
            self.localisation = self.get_bbox_2d_center()
        else:
            self.localisation = self.get_bbox_2d_centers()


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
    
    def get_bbox_2d_centers(self):
        centers = []
        if self.type_str == "LAS":
            classifications = np.unique(self.pc.classification)
            for cls in classifications:
                mask = self.pc.classification == cls
                xs = self.pc.x[mask]
                ys = self.pc.y[mask]
                zs = self.pc.z[mask]
                mean_x = (min(xs) + max(xs)) / 2
                mean_y = (min(ys) + max(ys)) / 2
                mean_z = (min(zs) + max(zs)) / 2
                if mean_x < 180 and mean_y < 90:
                    print("Point cloud seems to be in WGS84 coordinates, converting to LV95.")
                    mean_x, mean_y, mean_z = utils.convert_wgs84_to_lv95(mean_x, mean_y, mean_z)
                centers.append((mean_y, mean_x))
        elif self.type_str == "PLY":
            points = self.pc['vertex']
            data = points.data
            scalar_field = data[self.scalar_field_name]
            classifications = np.unique(scalar_field)
            for cls in classifications:
                mask = scalar_field == cls
                xs = data['x'][mask]
                ys = data['y'][mask]
                zs = data['z'][mask]
                mean_x = (min(xs) + max(xs)) / 2
                mean_y = (min(ys) + max(ys)) / 2
                mean_z = (min(zs) + max(zs)) / 2
                if mean_x < 180 and mean_y < 90:
                    print("Point cloud seems to be in WGS84 coordinates, converting to LV95.")
                    mean_x, mean_y, mean_z = utils.convert_wgs84_to_lv95(mean_x, mean_y, mean_z)
                centers.append((mean_y, mean_x))
        return centers
    
    def apply_label(self, pc_label: int):
        if self.type_str == "LAS":
            self.pc.classification[:] = int(pc_label.label)
        elif self.type_str == "PLY":
            vertex = self.pc['vertex']
            data = vertex.data

            if 'scalar_Classification' in data.dtype.names:
                data['scalar_Classification'][:] = float(pc_label.label)
            else:
                data = rfn.append_fields(
                    data,
                    'scalar_Classification',
                    np.full(data.shape, float(pc_label.label), dtype=np.float32),
                    usemask=False,
                    dtypes=[np.float32]
                )

            elements = []
            for el in self.pc.elements:
                if el.name == 'vertex':
                    elements.append(PlyElement.describe(data, 'vertex'))
                else:
                    elements.append(el)
            self.pc = PlyData(elements, text=self.pc.text)
            
    def store_pc(self, folder_path: str):
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