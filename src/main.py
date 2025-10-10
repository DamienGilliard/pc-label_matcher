import argparse
import os

import data_loader, matcher

def main(dir_depth: int):
    point_clouds = data_loader.load_las_files_from_directory('./data/point_clouds', depth=dir_depth)
    
    label_csv_files = [f for f in os.listdir('./data/labels') if f.endswith('.csv')]
    if not label_csv_files:
        raise FileNotFoundError("No CSV file found in ./data/labels/")
    label_csv_path = os.path.join('./data/labels', label_csv_files[0])
    labels = data_loader.load_labels_from_csv(label_csv_path, './class_table.csv')
    print(f"Loaded {len(labels)} labels and {len(point_clouds)} las files.")

    new_point_clouds = matcher.match_point_clouds_with_labels(point_clouds, labels)
    print(f"Matched {len(new_point_clouds)} point clouds with labels.")
    for new_pc in new_point_clouds:
        new_pc.store_las("./output_las")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process point clouds and labels.")
    parser.add_argument('--dir_depth', type=int, default=2, help='Depth of the directory to scan for LAS files.\nIf set to 1, all las files are supposed to be in the same directory.\nIf set to 2, all las files are supposed to be in subdirectories of the given directory.')
    args = parser.parse_args()
    dir_depth = args.dir_depth
    main(dir_depth)