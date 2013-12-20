import gdal
from gdalconst import GA_ReadOnly

import unittest
import os
import logging

class TestMyCode(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_gdal_load_raster_fixture_as_dataset(self):
        log = logging.getLogger(__name__)

        test_dir = os.path.dirname(os.path.realpath(__file__))
        fixtures_dir = os.path.join(test_dir, 'fixtures')
        raster_fixture_path = os.path.join(fixtures_dir, 'raster.tif')

        dataset = gdal.Open(raster_fixture_path, GA_ReadOnly)

        # We should have no error loading the dataset
        self.assertTrue(dataset != None)

        # Pixels wide
        self.assertEqual(dataset.RasterXSize, 886)
        # Pixels high
        self.assertEqual(dataset.RasterYSize, 691)

        # The raster band
        band = dataset.GetRasterBand(1)

        # The raster band type (should be Float64)
        self.assertEqual(gdal.GetDataTypeName(band.DataType), "Float64")

        # The minimum value in the band
        self.assertEqual(band.GetMinimum(), 0)
        # The maximum value in the band
        self.assertEqual(band.GetMaximum(), 0.62908011869436)

        # The min and max can also be calculated this way
        (imin,imax) = band.ComputeRasterMinMax(1)
        self.assertEqual(imin, 0)
        self.assertEqual(imax, 0.62908011869436)

        # The scale of the raster should be 1 (0-1 scale)
        self.assertEqual(band.GetScale(), 1)

        # Get the transform object (provides access to position information)
        geotransform = dataset.GetGeoTransform()
        self.assertTrue(geotransform != None)

        # From GDAL Docs:
        #
        #adfGeoTransform[0] /* top left x */
        #adfGeoTransform[1] /* w-e pixel resolution */
        #adfGeoTransform[2] /* 0 */
        #adfGeoTransform[3] /* top left y */
        #adfGeoTransform[4] /* 0 */
        #adfGeoTransform[5] /* n-s pixel resolution (negative value) */

        origin_x = geotransform[0]
        origin_y = geotransform[3]

        pixel_size_x = geotransform[1]
        pixel_size_y = geotransform[5]

        # Origin = ( 111.975 , -9.975 )
        # Pixel Size = ( 0.05 , -0.05 )

        self.assertEqual(origin_x, 111.975)
        self.assertEqual(origin_y, -9.975)
        self.assertEqual(round(pixel_size_x, 6), 0.05)
        self.assertEqual(round(pixel_size_y, 6), -0.05)


    def test_gdal_load_a_missing_dataset(self):
        log = logging.getLogger(__name__)

        test_dir = os.path.dirname(os.path.realpath(__file__))
        fixtures_dir = os.path.join(test_dir, 'fixtures')
        raster_fixture_path = os.path.join(fixtures_dir, 'raster_no_such_file.tif')

        dataset = gdal.Open(raster_fixture_path, GA_ReadOnly)
        self.assertEqual(dataset, None)
