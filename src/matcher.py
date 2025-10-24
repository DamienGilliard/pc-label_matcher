"""
This module contains the functions that match point clouds with labels.
"""
import numpy as np

def match_point_clouds_with_labels(point_clouds, labels, max_distance=2.0):
    # Sort labels by their standard deviation norm (ascending)
    sorted_labels = sorted(labels, key=lambda lbl: lbl.get_std_dev_norm())
    matched_point_clouds = []

    if len(point_clouds) > 1:
        for lbl in sorted_labels:
            best_pc = None
            best_distance = float('inf')
            for pc in point_clouds:
                distance = np.linalg.norm(np.array(pc.localisation) - np.array(lbl.get_2d_location()))
                if distance < best_distance:
                    best_distance = distance
                    best_pc = pc
            if best_distance > max_distance:
                print(f"No suitable point cloud found for label at {lbl.geolocation} (best distance: {best_distance:.2f}m but max distance is {max_distance}m). Skipping this label.")
                continue
            best_pc.label = lbl
            best_pc.apply_label(lbl)
            matched_point_clouds.append(best_pc)
    return matched_point_clouds


def match_point_cloud_with_labels(point_cloud, labels, discriminative_scalar_field_name, max_distance=2.0):
    matched_scalar_field_values = {}
    for lbl in labels:
        if point_cloud.n_clusters > 1 and discriminative_scalar_field_name is not None:
            best_sfv = None
            best_distance = float('inf')
            for sfv, loc in point_cloud.localisations.items():
                distance = np.linalg.norm(np.array(loc) - np.array(lbl.get_2d_location()))
                if distance < best_distance:
                    best_distance = distance
                    best_sfv = sfv
            if best_distance > max_distance:
                print(f"No suitable segment found in point cloud for label at {lbl.geolocation} (best distance: {best_distance:.2f}m but max distance is {max_distance}m). Skipping this label.")
                continue
            matched_scalar_field_values[best_sfv] = lbl
        else:
            distance = np.linalg.norm(np.array(point_cloud.localisation) - np.array(lbl.get_2d_location()))
            if distance > max_distance:
                print(f"No suitable point cloud found for label at {lbl.geolocation} (distance: {distance:.2f}m but max distance is {max_distance}m). Skipping this label.")
                continue
    
    for sfv, lbl in matched_scalar_field_values.items():
        print(f"Applying label {lbl.label} to segment with scalar field value {sfv}.")
        point_cloud.apply_label_to_scalar_field(sfv, lbl)
    return point_cloud