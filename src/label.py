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
        return (self.std_devs[0]**2 + self.std_devs[1]**2 + self.std_devs[2]**2) ** 0.5

    def get_2d_location(self):
        lv95_coords = utils.convert_wgs84_to_lv95(self.geolocation[0], self.geolocation[1], self.geolocation[2])
        return (lv95_coords[0], lv95_coords[1])

    def __repr__(self):
        return f"Label(label={self.label}, geolocation={self.geolocation}, std_devs={self.std_devs})"
