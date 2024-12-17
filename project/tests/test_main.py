import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

import numpy as np
import pydicom

from converter import Dicom2BmpConverter
from utils import setup_logging


class TestDicom2BmpConverter(unittest.TestCase):
    def setUp(self):
        self.input_dir = Path('/fake/input')
        self.output_dir = Path('/fake/output')
        self.converter = Dicom2BmpConverter(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            apply_windowing=True
        )

    @patch('converter.pydicom.dcmread')
    def test_is_dicom_file_true(self, mock_dcmread):
        mock_dcmread.return_value = MagicMock()
        filepath = Path('test.dcm')
        result = self.converter.is_dicom_file(filepath)
        self.assertTrue(result)
        mock_dcmread.assert_called_once_with(filepath, stop_before_pixels=True, force=True)

    @patch('converter.pydicom.dcmread', side_effect=Exception('Not a DICOM file'))
    def test_is_dicom_file_false(self, mock_dcmread):
        filepath = Path('test.txt')
        result = self.converter.is_dicom_file(filepath)
        self.assertFalse(result)
        mock_dcmread.assert_called_once_with(filepath, stop_before_pixels=True, force=True)

    @patch('converter.Image.fromarray')
    @patch('converter.pydicom.dcmread')
    def test_convert_single(self, mock_dcmread, mock_fromarray):
        # Setup mock DICOM dataset
        mock_ds = MagicMock()
        mock_ds.pixel_array = np.array([[0, 1], [2, 3]], dtype=np.int16)
        mock_ds.WindowCenter = 1
        mock_ds.WindowWidth = 2
        mock_dcmread.return_value = mock_ds

        # Setup mock Image
        mock_image = MagicMock()
        mock_fromarray.return_value = mock_image

        # Run conversion
        dcm_path = self.input_dir / 'test.dcm'
        self.converter.convert_single(dcm_path)

        # Assertions
        mock_dcmread.assert_called_once_with(dcm_path, force=True)
        mock_fromarray.assert_called_once()
        mock_image.save.assert_called_once_with(self.output_dir / 'test.bmp')


if __name__ == '__main__':
    setup_logging(verbosity=2)
    unittest.main()
