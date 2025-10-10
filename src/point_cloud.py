import utils

class PointCloud:
    """
    This class represents a point cloud with its associated data.
    """
    
    def __init__(self, las, pc_label=None):
        self.las = las
        self.localisation = self.get_bbox_2d_center()
        self.label = pc_label

    def get_bbox_2d_center(self):
        mean = (self.las.header.mins + self.las.header.maxs) / 2
        if mean[0] < 180 and mean[1] < 90:
            print("Point cloud seems to be in WGS84 coordinates, converting to LV95.")
            mean = utils.convert_wgs84_to_lv95(mean[0], mean[1], mean[2])
        return (mean[1], mean[0])
    
    def apply_label_to_las(self, pc_label):
        self.las.classification[:] = int(pc_label.label)
            
    def store_las(self, output_path):
        self.las.write(output_path)