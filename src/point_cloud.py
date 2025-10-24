import os

import numpy as np
import numpy.lib.recfunctions as rfn
from plyfile import PlyElement, PlyData

import utils

class PointCloud:
    """
    This class represents a point cloud with its associated data.
    """

    def __init__(self, pc, pc_label=None, type_str="LAS", discriminative_scalar_field_name=None):
        self.pc = pc
        self.type_str = type_str
        self.label = pc_label
        self.discriminative_scalar_field_name = discriminative_scalar_field_name
        if self.discriminative_scalar_field_name:
            if self.type_str == "LAS":
                self.n_clusters = len(np.unique(self.pc.classification))
            elif self.type_str == "PLY":
                if self.discriminative_scalar_field_name not in self.pc['vertex'].data.dtype.names:
                    raise ValueError(f"Scalar field '{self.discriminative_scalar_field_name}' not found in PLY point cloud.")
                self.n_clusters = len(np.unique(self.pc['vertex'][self.discriminative_scalar_field_name]))
        else:
            self.n_clusters = 1
        if self.n_clusters == 1:
            self.localisation = self.get_bbox_2d_center()
            self.localisations = None
        else:
            self.localisation = None
            self.localisations = self.get_bbox_2d_centers()


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
        """
        Get the 2D centers of the bounding boxes for each segment in the point cloud.

        Returns:
        dict: A dictionary mapping scalar field values to their corresponding (lat, lon) centers.
        """
        centers = {}
        if self.type_str == "PLY":
            points = self.pc['vertex']
            data = points.data
            scalar_field = data[self.discriminative_scalar_field_name]
            scalar_field_values = np.unique(scalar_field)
            for sfv in scalar_field_values:
                mask = scalar_field == sfv
                xs = data['x'][mask]
                ys = data['y'][mask]
                zs = data['z'][mask]
                mean_x = (min(xs) + max(xs)) / 2
                mean_y = (min(ys) + max(ys)) / 2
                mean_z = (min(zs) + max(zs)) / 2
                if mean_x < 180 and mean_y < 90:
                    print("Point cloud seems to be in WGS84 coordinates, converting to LV95.")
                    mean_x, mean_y, mean_z = utils.convert_wgs84_to_lv95(mean_x, mean_y, mean_z)
                centers[sfv] = (mean_y, mean_x)
            if 0 in centers:
                del centers[0]
                print("Removed segment with scalar field value 0 from localisations because it is assumed to be the ground.")
        else:
            raise NotImplementedError("get_bbox_2d_centers is only implemented for PLY point clouds.")
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

    def apply_label_to_scalar_field(self, scalar_field_value: int, pc_label: int):
        """
        applies a given label to all points in the point cloud with the given scalar field value
        """
        if self.type_str == "PLY":
            vertex = self.pc['vertex']
            data = vertex.data

            if 'scalar_Classification' in data.dtype.names:
                print("scalar_Classification field already exists in PLY point cloud. Updating values.")
                data['scalar_Classification'][data[self.discriminative_scalar_field_name] == scalar_field_value] = float(pc_label.label)

            else:
                print("scalar_Classification field does not exist in PLY point cloud. Creating new field.")
                data = rfn.append_fields(
                    data,
                    'scalar_Classification',
                    np.full(data.shape, float(-1), dtype=np.float32),
                    usemask=False,
                    dtypes=[np.float32]
                )
                data['scalar_Classification'][data[self.discriminative_scalar_field_name] == scalar_field_value] = float(pc_label.label)

            elements = []
            for el in self.pc.elements:
                if el.name == 'vertex':
                    elements.append(PlyElement.describe(data, 'vertex'))
                else:
                    elements.append(el)
            self.pc = PlyData(elements, text=self.pc.text)
        
        else:
            raise NotImplementedError("apply_label_to_scalar_field is only implemented for PLY point clouds.")

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