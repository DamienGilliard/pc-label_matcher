"""
This module provides functions to load data from las and CSV files.
"""
import os
import laspy
import plyfile
import label, utils, point_cloud

def load_pc_files_from_directory(directory_path, depth=1, scalar_field_name=None):
    """
    Load all .las or .ply files from the specified directory.

    Parameters:
    directory_path (str): The path to the directory containing .las or .ply files.
    depth (int): The depth of directory (0 if only one file is provided, 
                 1 if all files are in the same directory,
                 2 if all files are in subdirectories of directory_path).
    scalar_field_name (str): The name of the scalar field to load (if any).

    Returns:
    list: A list of point_cloud.PointCloud objects.
    """

    point_clouds = []
    if depth == 0:
        # Single file case
        filename = directory_path
        if filename.endswith('.las'):
            file_path = os.path.join(directory_path, filename)
            las_data = laspy.read(file_path)
            pc = point_cloud.PointCloud(las_data, type_str="LAS", scalar_field_name=scalar_field_name)
            return [pc]
        elif filename.endswith('.ply'):
            file_path = os.path.join(directory_path, filename)
            ply_data = plyfile.PlyData.read(file_path)
            pc = point_cloud.PointCloud(ply_data, type_str="PLY", scalar_field_name=scalar_field_name)
            return [pc]
    elif depth == 1:
        for filename in os.listdir(directory_path):
            if filename.endswith('.las'):
                file_path = os.path.join(directory_path, filename)
                las_data = laspy.read(file_path)
                pc = point_cloud.PointCloud(las_data, type_str="LAS")
                point_clouds.append(pc)
            elif filename.endswith('.ply'):
                file_path = os.path.join(directory_path, filename)
                ply_data = plyfile.PlyData.read(file_path)
                pc = point_cloud.PointCloud(ply_data, type_str="PLY")
                point_clouds.append(pc)
    elif depth == 2:
        for root, dirs, files in os.walk(directory_path):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                for filename in os.listdir(dir_path):
                    if filename.endswith('.las'):
                        file_path = os.path.join(dir_path, filename)
                        las_data = laspy.read(file_path)
                        pc = point_cloud.PointCloud(las_data)
                        point_clouds.append(pc)
                    elif filename.endswith('.ply'):
                        file_path = os.path.join(dir_path, filename)
                        ply_data = plyfile.PlyData.read(file_path)
                        pc = point_cloud.PointCloud(ply_data, type_str="PLY")
                        point_clouds.append(pc)
    return point_clouds

def load_labels_from_csv(labels_csv_path, classes_csv_path):
    """
    Load labels from a CSV file.

    Parameters:
    labels_csv_path (str): The path to the CSV file containing labels.
    classes_csv_path (str): The path to the CSV file containing the reference label table.

    Returns:
    list: A list of Label objects (see label module).
    """
    labels = []
    with open(labels_csv_path, 'r') as file:
        lines = file.readlines()
        if lines[0].strip() != "#Mean longitude;Mean latitude;Mean altitude;SNR;stddev longitude;stddev latitude;stddev altitude;stddev SNR; label":
            raise ValueError(f"Unexpected header format. Expected:\n'#Mean longitude;Mean latitude;Mean altitude;SNR;stddev longitude;stddev latitude;stddev altitude;stddev SNR; label', \ngot:\n'{lines[0].strip()}'")
        for line in lines[1:]:  # Skip header
            parts = line.strip().split(';')
            if len(parts) != 9:
                raise ValueError(f"Unexpected number of columns in line: {line.strip()}")
            line_label = label.Label(
                label=utils.get_label_index(parts[8], classes_csv_path),
                geolocation=(float(parts[0]), float(parts[1]), float(parts[2])),
                std_devs=(float(parts[4]), float(parts[5]), float(parts[6]))
            )
            labels.append(line_label)
    return labels
