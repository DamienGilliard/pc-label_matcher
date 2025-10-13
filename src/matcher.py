"""
This module contains the functions that match point clouds with labels.
"""
import numpy as np

def match_point_clouds_with_labels(las_point_clouds, labels, pc_to_label=True, max_distance=2.0):
    # Sort labels by their standard deviation norm (ascending)
    sorted_labels = sorted(labels, key=lambda lbl: lbl.get_std_dev_norm())

    if pc_to_label:
        print("Matching point clouds to labels...")
        for pc in las_point_clouds:
            best_label = None
            best_distance = float('inf')
            for lbl in sorted_labels:
                distance = np.linalg.norm(np.array(pc.localisation) - np.array(lbl.get_2d_location()))
                if distance < best_distance:
                    best_distance = distance
                    best_label = lbl
            if best_distance > max_distance:
                print(f"No suitable label found for point cloud at {pc.localisation} (best distance: {best_distance:.2f}m but max distance is {max_distance}m). Skipping this point cloud.")
                las_point_clouds.remove(pc)
                continue
            pc.label = best_label
            pc.apply_label_to_las(best_label)
    else:
        print("Matching labels to point clouds...")
        for lbl in sorted_labels:
            best_pc = None
            best_distance = float('inf')
            for pc in las_point_clouds:
                distance = np.linalg.norm(np.array(pc.localisation) - np.array(lbl.get_2d_location()))
                if distance < best_distance:
                    best_distance = distance
                    best_pc = pc
            if best_distance > max_distance:
                print(f"No suitable point cloud found for label at {lbl.geolocation} (best distance: {best_distance:.2f}m but max distance is {max_distance}m). Skipping this label.")
                continue
            best_pc.label = lbl
            best_pc.apply_label_to_las(lbl)
    return las_point_clouds
