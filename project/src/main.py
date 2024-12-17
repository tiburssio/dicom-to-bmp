import argparse
import logging
from pathlib import Path

from converter import Dicom2BmpConverter
from utils import setup_logging


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert DICOM files to BMP images.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help="Directory containing DICOM files."
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help="Directory to save BMP images."
    )
    parser.add_argument(
        '--window-center',
        type=int,
        default=40,
        help="Window center for DICOM visualization"
    )
    parser.add_argument(
        '--window-width',
        type=int,
        default=400,
        help="Window width for DICOM visualization"
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help="Number of files to process in each batch"
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='count',
        default=0,
        help="Increase output verbosity."
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    setup_logging(args.verbose)

    converter = Dicom2BmpConverter(
        input_dir=args.input,
        output_dir=args.output,
        window_center=args.window_center,
        window_width=args.window_width,
        batch_size=args.batch_size
    )
    converter.convert_all()


if __name__ == "__main__":
    main()
