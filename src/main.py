import data_loader, matcher

def main():
    point_clouds = data_loader.load_las_files_from_directory('./test_data', depth=2)
    labels = data_loader.load_labels_from_csv('./2025_10_06_aggregated_species_geolocation_and_labels.csv', './class_table.csv')
    print(f"Loaded {len(labels)} labels and {len(point_clouds)} las files.")

    new_point_clouds = matcher.match_point_clouds_with_labels(point_clouds, labels)
    print(f"Matched {len(new_point_clouds)} point clouds with labels.")
    for new_pc in new_point_clouds:
        output_path = f"./output_las/pc_with_label_at_{new_pc.localisation[0]}_{new_pc.localisation[1]}.las"
        new_pc.store_las(output_path)

if __name__ == "__main__":
    main()