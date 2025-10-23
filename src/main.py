import argparse
import os

import data_loader, matcher

def main(dir_depth: int, pc_to_label: bool, max_distance: float):
    point_clouds = data_loader.load_pc_files_from_directory('./data/point_clouds', depth=dir_depth)
    
    label_csv_files = [f for f in os.listdir('./data/labels') if f.endswith('.csv')]
    if not label_csv_files:
        raise FileNotFoundError("No CSV file found in ./data/labels/")
    label_csv_path = os.path.join('./data/labels', label_csv_files[0])
    labels = data_loader.load_labels_from_csv(label_csv_path, './class_table.csv')
    print(f"Loaded {len(labels)} labels and {len(point_clouds)} las files.")

    new_point_clouds = matcher.match_point_clouds_with_labels(point_clouds, labels, pc_to_label, max_distance)
    print(f"Matched {len(new_point_clouds)} point clouds with labels.")
    for new_pc in new_point_clouds:
        new_pc.store_pc("./output_pc")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process point clouds and labels.")
    parser.add_argument('--dir_depth', type=int, default=2, help='Depth of the directory to scan for LAS files.\n If set to 0, we suppose only one file is provided, and contains a scalar field that distinguishes the different segments\nIf set to 1, all las files are supposed to be in the same directory.\nIf set to 2, all las files are supposed to be in subdirectories of the given directory.')
    parser.add_argument('--scalar_field_name', type=str, default=None, help='Name of the scalar field to load from point clouds (if any). Default is None.')
    parser.add_argument('--pc_to_label', type=int, default=1, help='Whether to match point clouds to labels (1) or labels to point clouds (0). Default is 1.')
    parser.add_argument('--max_distance', type=float, default=2.0, help='Maximum distance for matching point clouds to labels (in meters). Default is 2.0.')
    args = parser.parse_args()
    dir_depth = args.dir_depth
    pc_to_label = bool(args.pc_to_label)
    max_distance = args.max_distance
    main(dir_depth, pc_to_label, max_distance)