import utils

class Label:
    """
    This class represents a label with its associated description and geolocation.
    """

    def __init__(self, label: int, geolocation: tuple, std_devs: tuple = (0.0, 0.0, 0.0)):
        self.label = label
        self.geolocation = geolocation
        self.std_devs = std_devs

    def get_std_dev_norm(self):
        return ((self.std_devs[0] * 111111)**2 + (self.std_devs[1] * 111111)**2 + self.std_devs[2]**2) ** 0.5 # Approx conversion of degrees to meters for lat/lon

    def get_2d_location(self, coord_system="LV95"):

        if coord_system == "LV95":
            if self.geolocation[0] < 180 and self.geolocation[1] < 90:
                lv95_coords = utils.convert_wgs84_to_lv95(self.geolocation[0], self.geolocation[1], self.geolocation[2])
                return (lv95_coords[0], lv95_coords[1])
            else:
                return (self.geolocation[0], self.geolocation[1])
        elif coord_system == "WGS84":
            if self.geolocation[0] > 180 and self.geolocation[1] > 90:
                wgs84_coords = utils.convert_lv95_to_wgs84(self.geolocation[0], self.geolocation[1], self.geolocation[2])
                return (wgs84_coords[0], wgs84_coords[1])
            else:
                return (self.geolocation[0], self.geolocation[1])
        else:
            raise ValueError(f"Unknown coordinate system: {coord_system}")

    def __repr__(self):
        return f"Label(label={self.label}, geolocation={self.geolocation}, std_devs={self.std_devs})"
