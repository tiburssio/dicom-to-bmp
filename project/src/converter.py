import logging
from pathlib import Path

import numpy as np
import pydicom
from PIL import Image, ImageDraw, ImageFont
import datetime


class Dicom2BmpConverter:
    """
    Class for converting DICOM files to BMP images, even without the .dcm extension.

    Attributes:
        input_dir (Path): Directory containing DICOM files.
        output_dir (Path): Directory where BMP files will be saved.
        window_center (int): Window center for DICOM visualization.
        window_width (int): Window width for DICOM visualization.
        batch_size (int): Number of files to process in each batch.
    """

    def __init__(self, input_dir: Path, output_dir: Path, window_center: int = 40, window_width: int = 400, batch_size: int = 50):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.window_center = window_center
        self.window_width = window_width
        self.batch_size = batch_size
        self.apply_windowing = True

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Output directory set to: {self.output_dir}")

    def is_dicom_file(self, filepath: Path) -> bool:
        """Check if a file is a valid DICOM file."""
        try:
            pydicom.dcmread(filepath, stop_before_pixels=True, force=True)
            return True
        except Exception as e:
            logging.debug(f"Not a DICOM file: {filepath} - {str(e)}")
            return False

    def _apply_windowing(self, ds: pydicom.dataset.FileDataset, pixel_array: np.ndarray) -> np.ndarray:
        """
        Aplica Window Center e Window Width mantendo a escala original.
        """
        try:
            # Primeiro, vamos verificar se a imagem precisa ser reescalada
            if hasattr(ds, 'RescaleIntercept') and hasattr(ds, 'RescaleSlope'):
                pixel_array = pixel_array * float(ds.RescaleSlope) + float(ds.RescaleIntercept)
            
            window_center = float(self.window_center)
            window_width = float(self.window_width)

            if hasattr(ds, 'WindowCenter') and hasattr(ds, 'WindowWidth'):
                window_center = float(ds.WindowCenter) if not isinstance(ds.WindowCenter, (list, tuple)) else float(ds.WindowCenter[0])
                window_width = float(ds.WindowWidth) if not isinstance(ds.WindowWidth, (list, tuple)) else float(ds.WindowWidth[0])

            # Garantir que a largura da janela seja pelo menos 1
            window_width = max(window_width, 1)
            
            # Calcular limites da janela
            lower = window_center - (window_width / 2.0)
            upper = window_center + (window_width / 2.0)
            
            # Aplicar os limites da janela
            windowed = np.clip(pixel_array, lower, upper)
            
            return windowed
            
        except Exception as e:
            logging.error(f"Error in windowing: {str(e)}")
            return pixel_array

    def _normalize_to_8bit(self, pixel_array: np.ndarray) -> np.ndarray:
        """
        Normaliza mantendo a resolução original.
        """
        try:
            # Converter para float64 para maior precisão
            pixel_array = pixel_array.astype(float)
            
            min_val = np.min(pixel_array)
            max_val = np.max(pixel_array)
            
            if max_val == min_val:
                return np.zeros_like(pixel_array, dtype=np.uint8)
            
            # Normalização mais precisa
            normalized = ((pixel_array - min_val) * 255.0 / (max_val - min_val))
            
            # Garantir que os valores estejam no intervalo correto
            normalized = np.clip(normalized, 0, 255)
            
            return normalized.astype(np.uint8)
            
        except Exception as e:
            logging.error(f"Error in normalization: {str(e)}")
            return np.zeros_like(pixel_array, dtype=np.uint8)

    def _get_metadata_text(self, ds: pydicom.dataset.FileDataset) -> dict:
        """Extrai informações relevantes dos metadados DICOM."""
        metadata = {}
        
        # Informações do paciente
        try:
            metadata['patient_name'] = str(getattr(ds, 'PatientName', '')).strip()
            metadata['patient_id'] = str(getattr(ds, 'PatientID', '')).strip()
            metadata['patient_birth_date'] = str(getattr(ds, 'PatientBirthDate', '')).strip()
            
            # Formatando a data de nascimento
            if metadata['patient_birth_date']:
                try:
                    birth_date = datetime.datetime.strptime(metadata['patient_birth_date'], '%Y%m%d')
                    metadata['patient_birth_date'] = birth_date.strftime('%d/%m/%Y')
                except:
                    pass
        except:
            logging.warning("Erro ao extrair informações do paciente")

        # Informações do estudo
        try:
            metadata['study_date'] = str(getattr(ds, 'StudyDate', '')).strip()
            if metadata['study_date']:
                try:
                    study_date = datetime.datetime.strptime(metadata['study_date'], '%Y%m%d')
                    metadata['study_date'] = study_date.strftime('%d/%m/%Y')
                except:
                    pass
            
            metadata['study_description'] = str(getattr(ds, 'StudyDescription', '')).strip()
            metadata['series_description'] = str(getattr(ds, 'SeriesDescription', '')).strip()
        except:
            logging.warning("Erro ao extrair informações do estudo")

        # Informações técnicas
        try:
            metadata['institution_name'] = str(getattr(ds, 'InstitutionName', '')).strip()
            metadata['manufacturer'] = str(getattr(ds, 'Manufacturer', '')).strip()
            metadata['slice_thickness'] = str(getattr(ds, 'SliceThickness', '')).strip()
            metadata['kvp'] = str(getattr(ds, 'KVP', '')).strip()
            metadata['window_center'] = str(getattr(ds, 'WindowCenter', '')).strip()
            metadata['window_width'] = str(getattr(ds, 'WindowWidth', '')).strip()
        except:
            logging.warning("Erro ao extrair informações técnicas")

        return metadata

    def _add_overlay_text(self, image: Image.Image, metadata: dict) -> Image.Image:
        """Adiciona texto de overlay à imagem com tamanho adaptativo."""
        try:
            # Criar uma cópia da imagem para desenhar
            img_with_text = image.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            # Calcular tamanho da fonte baseado na dimensão da imagem
            image_size = min(image.width, image.height)
            font_size = max(int(image_size * 0.02), 8)  # Mínimo de 8px, máximo de 2% da imagem
            
            # Tentar usar uma fonte do sistema, com fallback para fonte padrão
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            # Cor do texto (branco)
            text_color = 255
            
            # Calcular margens baseadas no tamanho da imagem
            margin = int(image_size * 0.01)  # 1% da imagem
            
            # Verificar se a imagem é pequena (menor que 256x256)
            is_small_image = image_size < 256
            
            if is_small_image:
                # Para imagens pequenas, mostrar apenas informações essenciais
                essential_info = []
                if metadata.get('patient_name'):
                    essential_info.append(metadata['patient_name'])
                if metadata.get('study_date'):
                    essential_info.append(metadata['study_date'])
                
                # Posicionar no topo da imagem
                y_position = margin
                for line in essential_info:
                    text_width = draw.textlength(line, font=font)
                    x_position = (image.width - text_width) // 2  # Centralizar
                    draw.text((x_position, y_position), line, fill=text_color, font=font)
                    y_position += font_size + 2
                
            else:
                # Para imagens maiores, mostrar todas as informações
                # Informações do paciente (canto superior esquerdo)
                patient_info = []
                if metadata.get('patient_name'):
                    patient_info.append(f"Nome: {metadata['patient_name']}")
                if metadata.get('patient_id'):
                    patient_info.append(f"ID: {metadata['patient_id']}")
                if metadata.get('patient_birth_date'):
                    patient_info.append(f"Nasc.: {metadata['patient_birth_date']}")

                # Desenhar informações do paciente
                y_position = margin
                for line in patient_info:
                    draw.text((margin, y_position), line, fill=text_color, font=font)
                    y_position += font_size + 2

                # Informações do estudo (canto superior direito)
                study_info = []
                if metadata.get('study_date'):
                    study_info.append(f"Data: {metadata['study_date']}")
                if metadata.get('study_description'):
                    study_info.append(f"Estudo: {metadata['study_description']}")
                if metadata.get('series_description'):
                    study_info.append(f"Série: {metadata['series_description']}")

                # Desenhar informações do estudo
                y_position = margin
                for line in study_info:
                    text_width = draw.textlength(line, font=font)
                    draw.text((image.width - text_width - margin, y_position), 
                             line, fill=text_color, font=font)
                    y_position += font_size + 2

                # Informações técnicas (canto inferior)
                tech_info = []
                if metadata.get('institution_name'):
                    tech_info.append(f"Instituição: {metadata['institution_name']}")
                if metadata.get('manufacturer'):
                    tech_info.append(f"Fabricante: {metadata['manufacturer']}")
                if metadata.get('slice_thickness'):
                    tech_info.append(f"Espessura: {metadata['slice_thickness']}mm")
                if metadata.get('kvp'):
                    tech_info.append(f"kVp: {metadata['kvp']}")

                # Desenhar informações técnicas
                y_position = image.height - (len(tech_info) * (font_size + 2)) - margin
                for line in tech_info:
                    draw.text((margin, y_position), line, fill=text_color, font=font)
                    y_position += font_size + 2

            return img_with_text
        except Exception as e:
            logging.error(f"Erro ao adicionar overlay: {str(e)}")
            return image

    def convert_single(self, dcm_path: Path):
        """Convert a single DICOM file to BMP with overlay information."""
        try:
            # Read DICOM file
            ds = pydicom.dcmread(dcm_path, force=True)
            
            # Get original pixel array and convert to float64
            pixel_array = ds.pixel_array.astype(np.float64)
            
            logging.debug(f"Original image shape: {pixel_array.shape}")
            
            # Apply windowing
            if self.apply_windowing:
                pixel_array = self._apply_windowing(ds, pixel_array)
            
            # Normalize to 8-bit
            pixel_array = self._normalize_to_8bit(pixel_array)
            
            # Create PIL Image maintaining original size
            image = Image.fromarray(pixel_array, mode='L')
            
            # Get metadata
            metadata = self._get_metadata_text(ds)
            
            # Add overlay text
            image_with_overlay = self._add_overlay_text(image, metadata)
            
            # Create output filename
            output_filename = dcm_path.name + '.bmp'
            output_path = self.output_dir / output_filename
            
            # Save as BMP with maximum quality
            image_with_overlay.save(output_path, quality=100)
            logging.info(f"Converted: {dcm_path.name} -> {output_filename}")
            
        except Exception as e:
            logging.error(f"Error converting '{dcm_path}': {str(e)}")
            raise

    def convert_all(self):
        """Convert all DICOM files in the input directory to BMP format."""
        logging.info(f"Scanning for DICOM files in: {self.input_dir}")
        all_files = list(self.input_dir.glob('*'))
        dicom_files = [f for f in all_files if f.is_file() and self.is_dicom_file(f)]

        if not dicom_files:
            logging.warning(f"No DICOM files found in: {self.input_dir}")
            return

        logging.info(f"Found {len(dicom_files)} DICOM files to convert.")
        
        # Process files in batches
        for i in range(0, len(dicom_files), self.batch_size):
            batch = dicom_files[i:i + self.batch_size]
            for dcm_path in batch:
                try:
                    self.convert_single(dcm_path)
                except Exception as e:
                    logging.error(f"Error converting '{dcm_path}': {str(e)}")
                    continue
