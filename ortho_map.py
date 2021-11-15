#!/usr/bin/env python

class OrthoMap:

    def __init__(self, lon_range, lat_range, image, offset = [0, 0]):
        self.lon_range = [l + offset[0] for l in lon_range]
        self.lat_range = [l + offset[1] for l in lat_range]
        self.image = image
        self.offset = offset

    def plot(self, plt, ax):
        img = plt.imread(self.image)
        ax.imshow(img, extent=[self.lon_range[0], self.lon_range[1], self.lat_range[0], self.lat_range[1]])