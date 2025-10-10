import os
import sys
include_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'src'))
sys.path.insert(0, include_path)
import utils

def test_wgs84_to_lv95_and_back():
    # Test coordinates (Bern, Switzerland)
    lat, lon, alt = 46.94809, 7.44744, 540.0

    # Convert WGS84 to LV95
    x, y, z = utils.convert_wgs84_to_lv95(lat, lon, alt)

    # Convert back from LV95 to WGS84
    lat_converted, lon_converted, alt_converted = utils.convert_lv95_to_wgs84(x, y, z)

    # Assert that the converted coordinates are close to the original ones
    assert abs(lat - lat_converted) < 1e-5
    assert abs(lon - lon_converted) < 1e-5
    assert abs(alt - alt_converted) < 0.1
    print("WGS84 to LV95 and back conversion test passed.")

if __name__ == "__main__":
    test_wgs84_to_lv95_and_back()