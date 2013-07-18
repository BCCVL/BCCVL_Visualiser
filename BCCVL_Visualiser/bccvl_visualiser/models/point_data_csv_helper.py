import mapscript
import os
import logging
import csv
import bisect

#from scipy.interpolate import griddata
#from matplotlib.pyplot as plt

from bccvl_visualiser.models import TextWrapper
from bccvl_visualiser.models.mapscript_helper import MapScriptHelper

from bccvl_visualiser.models.api import (
    BaseAPI
    )

class PointDataCSV(object):

    def __init__(self, file_path, x_column_name='longitude', y_column_name='latitude'):
        """ Initialisation function for PointDataCSV

            Takes 3 arguments:
                file_path: the file path to the point data csv file
                x_column_name: the column name of the x values
                y_column_name: the column name of the y values
        """
        self.file_path = file_path
        self.x_column_name = x_column_name
        self.y_column_name = y_column_name

        self._determine_column_position()

    def _set_column_position(self):
        """ Inspect the column header, and store the index positions
            for the x and y columns
        """

        with open(self.file_path, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            header = reader.next()

            for idx, column in header:
                if column == self.x_column_name:
                    self.x_column_position = idx
                elif column == self.y_column_name:
                    self.y_column_position = idx

            if self.x_column_position == None:
                raise ValueError("Couldn't find the x column with name: %s", self.x_column_name)
            elif self.y_column_position == None:
                raise ValueError("Couldn't find the y column with name: %s", self.y_column_name)

    def _log_file_contents(self):
        log = logging.getLogger(__name__)
        with open(self.file_path, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            header = reader.next()

            for row in reader:
                log.debug(', '.join(row))

    def snap_to_grid(self):
        raise NotImplementedError("TODO, implement snap to grid")


#def snap(myGrid, myValue):
#    ix = bisect.bisect_right(myGrid, myValue)
#    if ix == 0:
#        return myGrid[0]
#    elif ix == len(myGrid):
#        return myGrid[-1]
#    else:
#        return min(myGrid[ix - 1], myGrid[ix], key=lambda gridValue: abs(gridValue - myValue))

