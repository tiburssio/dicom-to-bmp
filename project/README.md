# DICOM to BMP Converter

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)

</div>

## 🎯 Overview

The DICOM to BMP Converter is a robust and efficient Python tool designed to convert DICOM (Digital Imaging and Communications in Medicine) files to BMP (Bitmap) images. This tool is particularly useful for medical professionals and researchers who need to visualize medical images without specialized software.

## ✨ Key Features

- **Batch Processing**: Process multiple DICOM files simultaneously
- **Window Adjustment**: Support for window center/width for better visualization
- **Configurable Logging**: Different levels of execution logging detail
- **Error Handling**: Robust exception handling system
- **Cross-platform**: Compatible with Windows, Linux, and macOS
- **High Performance**: Optimized for efficient processing of large image volumes

## 🔧 System Requirements

- Python 3.7 or higher
- Main dependencies:
  - pydicom 3.0.1+
  - Pillow 11.0.0+
  - NumPy 2.2.0+
  - pylibjpeg 2.0.1+

## 🚀 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/dicom-to-bmp.git
   cd dicom-to-bmp
   ```

2. **Set Up Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## 💡 How to Use

### Basic Command Line

```bash
python src/main.py --input /path/to/dicoms --output /path/to/output
```

### Advanced Options

```bash
python src/main.py \
  --input /path/to/dicoms \
  --output /path/to/output \
  --window-center 40 \
  --window-width 400 \
  --verbose \
  --batch-size 50
```

### Available Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--input` | Directory with DICOM files | Required |
| `--output` | Directory to save BMPs | Required |
| `--window-center` | Visualization window center | Auto |
| `--window-width` | Visualization window width | Auto |
| `--verbose` | Enable detailed logs | False |
| `--batch-size` | Batch size for processing | 10 |

## 📊 Usage Examples

### Simple Conversion
```python
from dicom_converter import DicomConverter

converter = DicomConverter()
converter.convert("image.dcm", "output.bmp")
```

### Batch Processing
```python
converter = DicomConverter(batch_size=50)
converter.convert_directory("/dicoms", "/bmps")
```

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add: new feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

- Alexandre Leal - [@alexandre_fleal](https://x.com/alexandre_fleal)

## 🙏 Acknowledgments

- [pydicom](https://github.com/pydicom/pydicom) for the excellent DICOM manipulation library
- [Pillow](https://python-pillow.org/) for robust image processing support
- The entire open source community contributing to the tools used in this project

---

<div align="center">
Made with ❤️ by [Tiburssio](https://github.com/tiburssio)
</div>