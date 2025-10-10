"""
Several utils functions for point cloud processing and coordinates transformations.
"""

def convert_wgs84_to_lv95(lat, lon, alt):
    """
    Convert coordinates from WGS84 (degrees) to LV95.

    Parameters:
    lat (float): Latitude in degrees (WGS84).
    lon (float): Longitude in degrees (WGS84).
    alt (float): Altitude in meters (WGS84).

    Returns:
    tuple: A tuple containing x, y, z coordinates in LV95.
    """
    # according to https://backend.swisstopo.admin.ch/fileservice/sdweb-docs-prod-swisstopoch-files/files/2023/11/14/7f7bf15b-22e2-48b6-b1ab-6905f81dca8a.pdf 
    # the conversion from WGS84 to CH1903/LV95 is done by the following formulas

    # Conversion from degrees to arcseconds
    lat_arcsec = lat * 3600
    lon_arcsec = lon * 3600

    # Calculation of auxiliary values
    phi = (lat_arcsec - 169028.66) / 10000
    lambda_ = (lon_arcsec - 26782.5) / 10000

    # Calculation of the coordinates
    y = 2600072.37 + 211455.93 * lambda_ - 10938.51 * lambda_ * phi - 0.36 * lambda_ * phi * phi - 44.54 * lambda_ ** 3
    x = 1200147.07 + 308807.95 * phi + 3745.25 * lambda_ ** 2 + 76.63 * phi ** 2 - 194.56 * lambda_ ** 2 * phi + 119.79 * phi ** 3
    z = alt - 49.55 + 2.73 * lambda_ + 6.94 * phi

    return x, y, z


def convert_lv95_to_wgs84(x, y, z):
    """
    Convert coordinates from LV95 to WGS84 (degrees).

    Parameters:
    x (float): X coordinate in LV95.
    y (float): Y coordinate in LV95.
    z (float): Z coordinate in LV95.

    Returns:
    tuple: A tuple containing latitude, longitude in degrees and altitude in meters (WGS84).
    """

    # Calculation of auxiliary values
    y_aux = (y - 2600000) / 1000000
    x_aux = (x - 1200000) / 1000000

    # Calculation of latitude
    lat = 16.9023892 + 3.238272 * x_aux - 0.270978 * y_aux ** 2 - 0.002528 * x_aux ** 2 - 0.0447 * y_aux ** 2 * x_aux - 0.0140 * x_aux ** 3
    lat = lat * 100 / 36

    # Calculation of longitude
    lon = 2.6779094 + 4.728982 * y_aux + 0.791484 * y_aux * x_aux + 0.1306 * y_aux * x_aux ** 2 - 0.0436 * y_aux ** 3
    lon = lon * 100 / 36

    # Calculation of altitude
    alt = z + 49.55 - 12.60 * y_aux - 22.64 * x_aux

    return lat, lon, alt

def get_label_name(label_index:int, csv_table_path:str) -> str:
    """
    Get the label name from a CSV table given its index.

    Parameters:
    label_index (int): The index of the label.
    csv_table_path (str): The path to the CSV file containing the label table.

    Returns:
    str: The name of the label corresponding to the given index.
    """
    with open(csv_table_path, 'r') as file:
        labels_dict = {}
        lines = file.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split(';')
            labels_dict[int(parts[0])] = parts[1]
    return labels_dict.get(label_index, "Unknown")

def get_label_index(label_name:str, csv_table_path:str) -> int:
    """
    Get the label index from a CSV table given its name.

    Parameters:
    label_name (str): The name of the label.
    csv_table_path (str): The path to the CSV file containing the label table.

    Returns:
    int: The index of the label corresponding to the given name.
    """
    with open(csv_table_path, 'r') as file:
        labels_dict = {}
        lines = file.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split(';')
            labels_dict[parts[1]] = int(parts[0])
    return labels_dict.get(label_name, -1)