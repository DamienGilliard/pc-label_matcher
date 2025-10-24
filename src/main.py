import argparse
import os

import data_loader, matcher

def main(dir_depth: int, max_distance: float, scalar_field_name: str):
    point_clouds = data_loader.load_pc_files_from_directory('./data/point_clouds', depth=dir_depth, scalar_field_name=scalar_field_name)
    
    label_csv_files = [f for f in os.listdir('./data/labels') if f.endswith('.csv')]
    if not label_csv_files:
        raise FileNotFoundError("No CSV file found in ./data/labels/")
    label_csv_path = os.path.join('./data/labels', label_csv_files[0])
    labels = data_loader.load_labels_from_csv(label_csv_path, './class_table.csv')
    print(f"Loaded {len(labels)} labels and {len(point_clouds)} point cloud files.")

    if dir_depth == 0:
        new_point_cloud = matcher.match_point_cloud_with_labels(point_clouds[0], labels, scalar_field_name, max_distance)
        print("Matched point cloud with labels.")
        new_point_cloud.store_pc("./output_pc")
    else:
        new_point_clouds = matcher.match_point_clouds_with_labels(point_clouds, labels, max_distance)
        print(f"Matched {len(new_point_clouds)} point clouds with labels.")
        for new_pc in new_point_clouds:
            new_pc.store_pc("./output_pc")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process point clouds and labels.")
    parser.add_argument('--dir_depth', type=int, default=2, help='Depth of the directory to scan for LAS files.\n If set to 0, we suppose only one file is provided, and contains a scalar field that distinguishes the different segments\nIf set to 1, all las files are supposed to be in the same directory.\nIf set to 2, all las files are supposed to be in subdirectories of the given directory.')
    parser.add_argument('--scalar_field_name', type=str, default=None, help='Name of the scalar field that distinguishes the different segments in the point cloud (if any). Default is None.')
    parser.add_argument('--max_distance', type=float, default=2.0, help='Maximum distance for matching point clouds to labels (in meters). Default is 2.0.')
    args = parser.parse_args()
    dir_depth = args.dir_depth
    scalar_field_name = args.scalar_field_name
    max_distance = args.max_distance
    main(dir_depth, max_distance, scalar_field_name)