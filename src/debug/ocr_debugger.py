"""
OCR Accuracy Debugging Framework
Focus on legal document processing accuracy
"""

import cv2
import numpy as np
import pytesseract
from paddleocr import PaddleOCR
import json
from pathlib import Path
from difflib import SequenceMatcher
import logging
from datetime import datetime

class OCRDebugger:
    def __init__(self):
        self.tesseract = pytesseract
        self.paddle = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True)
        self.debug_dir = Path("./debug_output")
        self.debug_dir.mkdir(exist_ok=True)
        
        # Setup detailed logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ocr_debug.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def debug_ocr_pipeline(self, image_path, ground_truth_path=None):
        """Complete OCR debugging with visual output"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'image': str(image_path),
            'preprocessing_steps': [],
            'ocr_results': {},
            'accuracy_metrics': {}
        }
        
        # Load image
        img = cv2.imread(str(image_path))
        original = img.copy()
        
        # Step 1: Preprocessing visualization
        preprocessed_images = self.visualize_preprocessing(img)
        
        # Step 2: Run multiple OCR engines
        for prep_name, prep_img in preprocessed_images.items():
            # Save preprocessed image for inspection
            debug_img_path = self.debug_dir / f"{Path(image_path).stem}_{prep_name}.png"
            cv2.imwrite(str(debug_img_path), prep_img)

            # Tesseract OCR
            tess_result = pytesseract.image_to_data(prep_img, output_type=pytesseract.Output.DICT)
            
            # PaddleOCR
            paddle_result = self.paddle.ocr(np.array(prep_img), cls=True)
            
            results['ocr_results'][prep_name] = {
                'tesseract': self.parse_tesseract_result(tess_result),
                'paddle': self.parse_paddle_result(paddle_result)
            }
            
            # Visualize bounding boxes
            self.visualize_ocr_results(prep_img, tess_result, paddle_result, prep_name)
        
        # Step 3: Accuracy analysis if ground truth provided
        if ground_truth_path:
            with open(ground_truth_path, 'r') as f:
                ground_truth = f.read()
            
            for prep_name, ocr_data in results['ocr_results'].items():
                for engine, text in ocr_data.items():
                    accuracy = self.calculate_accuracy(text, ground_truth)
                    results['accuracy_metrics'][f"{prep_name}_{engine}"] = accuracy
        
        # Save detailed results
        with open(self.debug_dir / f"{Path(image_path).stem}_debug.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def calculate_accuracy(self, ocr_text, ground_truth):
        """Calculate detailed accuracy metrics"""
        # Clean texts
        ocr_clean = ' '.join(ocr_text.split())
        truth_clean = ' '.join(ground_truth.split())
        
        # Character-level accuracy
        char_accuracy = SequenceMatcher(None, ocr_clean, truth_clean).ratio()
        
        # Word-level accuracy
        ocr_words = set(ocr_clean.split())
        truth_words = set(truth_clean.split())
        word_accuracy = len(ocr_words & truth_words) / len(truth_words) if truth_words else 0
        
        return {
            'character_accuracy': char_accuracy,
            'word_accuracy': word_accuracy,
            'total_characters': len(truth_clean),
            'total_words': len(truth_words),
            'missed_words': list(truth_words - ocr_words)
        }
