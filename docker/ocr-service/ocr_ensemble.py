"""
OCR Ensemble Service with Confidence-Weighted Voting
Implements advanced voting mechanism with per-engine confidence scores
"""

import asyncio
import cv2
import json
import numpy as np
import time
import uuid
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import Counter

import torch
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import easyocr
import paddleocr
from rapidfuzz import fuzz, process
from PIL import Image
import redis
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis for job queue
redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

# Initialize OCR models with GPU support
device = 'cuda' if torch.cuda.is_available() else 'cpu'
logger.info(f"Using device: {device}")

# Initialize models
doctr_model = ocr_predictor(pretrained=True).to(device)
easy_reader = easyocr.Reader(['en'], gpu=(device == 'cuda'))
paddle_ocr = paddleocr.PaddleOCR(
    use_angle_cls=True, 
    lang='en', 
    use_gpu=(device == 'cuda'),
    show_log=False
)
@dataclass
class OCRResult:
    text: str
    confidence: float
    engine: str
    bbox: Optional[List[float]] = None

class ConfidenceWeightedVoter:
    """Implements confidence-weighted voting for OCR ensemble"""
    
    def __init__(self, min_confidence: float = 0.7):
        self.min_confidence = min_confidence
        
    def vote(self, results: List[OCRResult]) -> Tuple[str, float]:
        """
        Perform confidence-weighted voting on OCR results
        Returns: (voted_text, average_confidence)
        """
        if not results:
            return "", 0.0
            
        # Group results by similar text
        text_groups = {}
        for result in results:
            if result.confidence < self.min_confidence:
                continue
                
            # Find similar text group
            matched = False
            for group_text in text_groups:
                similarity = fuzz.ratio(result.text, group_text)
                if similarity > 85:  # 85% similarity threshold
                    text_groups[group_text].append(result)
                    matched = True
                    break
                    
            if not matched:
                text_groups[result.text] = [result]
        
        # Calculate weighted scores for each group
        group_scores = {}
        for text, group_results in text_groups.items():
            # Weight by confidence and number of engines agreeing
            total_confidence = sum(r.confidence for r in group_results)
            engine_bonus = len(set(r.engine for r in group_results)) * 0.1
            group_scores[text] = total_confidence * (1 + engine_bonus)
        
        # Select best candidate
        if not group_scores:
            return "", 0.0
            
        best_text = max(group_scores, key=group_scores.get)
        avg_confidence = np.mean([r.confidence for r in text_groups[best_text]])        return best_text, avg_confidence

class OCREngine:
    """Main OCR processing engine with ensemble capabilities"""
    
    def __init__(self):
        self.voter = ConfidenceWeightedVoter()
        self.preprocessing_enabled = True
        
    def preprocess_image(self, image_path: Path) -> np.ndarray:
        """Advanced image preprocessing for better OCR accuracy"""
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Binarization with adaptive threshold
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary    
    def ocr_with_doctr(self, image_path: Path) -> List[OCRResult]:
        """Process image with docTR and extract confidence scores"""
        try:
            doc = DocumentFile.from_images(str(image_path))
            result = doctr_model(doc)
            
            ocr_results = []
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            ocr_results.append(OCRResult(
                                text=word.value,
                                confidence=word.confidence,
                                engine="doctr",
                                bbox=[word.geometry[0][0], word.geometry[0][1], 
                                      word.geometry[1][0], word.geometry[1][1]]
                            ))
            return ocr_results
        except Exception as e:
            logger.error(f"docTR error: {e}")
            return []
    
    def ocr_with_easyocr(self, image_path: Path) -> List[OCRResult]:
        """Process image with EasyOCR and extract confidence scores"""
        try:
            results = easy_reader.readtext(str(image_path))
            ocr_results = []
            for bbox, text, confidence in results:
                ocr_results.append(OCRResult(
                    text=text,
                    confidence=confidence,
                    engine="easyocr",
                    bbox=[bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]]
                ))
            return ocr_results
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return []    
    def ocr_with_paddle(self, image_path: Path) -> List[OCRResult]:
        """Process image with PaddleOCR and extract confidence scores"""
        try:
            result = paddle_ocr.ocr(str(image_path), cls=True)
            ocr_results = []
            
            if result and result[0]:
                for line in result[0]:
                    bbox, (text, confidence) = line
                    ocr_results.append(OCRResult(
                        text=text,
                        confidence=confidence,
                        engine="paddle",
                        bbox=[bbox[0][0], bbox[0][1], bbox[2][0], bbox[2][1]]
                    ))
            return ocr_results
        except Exception as e:
            logger.error(f"PaddleOCR error: {e}")
            return []
    
    async def process_image(self, image_path: Path) -> Dict:
        """Process image with all OCR engines and perform weighted voting"""
        start_time = time.time()
        
        # Preprocess image if enabled
        if self.preprocessing_enabled:
            processed_img = self.preprocess_image(image_path)
            temp_path = image_path.with_suffix('.processed.png')
            cv2.imwrite(str(temp_path), processed_img)
            process_path = temp_path
        else:
            process_path = image_path
        
        # Run all OCR engines in parallel
        tasks = [
            asyncio.to_thread(self.ocr_with_doctr, process_path),
            asyncio.to_thread(self.ocr_with_easyocr, process_path),
            asyncio.to_thread(self.ocr_with_paddle, process_path)
        ]
        
        results = await asyncio.gather(*tasks)        
        # Flatten results and group by position
        all_results = [r for engine_results in results for r in engine_results]
        
        # Group results by spatial proximity
        position_groups = self._group_by_position(all_results)
        
        # Vote on each position group
        final_text = []
        confidences = []
        
        for group in position_groups:
            text, confidence = self.voter.vote(group)
            if text:
                final_text.append(text)
                confidences.append(confidence)
        
        # Clean up temporary file
        if self.preprocessing_enabled and temp_path.exists():
            temp_path.unlink()
        
        processing_time = time.time() - start_time
        
        return {
            "text": " ".join(final_text),
            "average_confidence": np.mean(confidences) if confidences else 0.0,
            "word_count": len(final_text),
            "processing_time": processing_time,
            "engines_used": ["doctr", "easyocr", "paddle"],
            "timestamp": time.time()
        }
    
    def _group_by_position(self, results: List[OCRResult]) -> List[List[OCRResult]]:
        """Group OCR results by spatial proximity"""
        if not results:
            return []
        
        # Sort by y-coordinate first, then x-coordinate
        sorted_results = sorted(results, key=lambda r: (r.bbox[1], r.bbox[0]) if r.bbox else (0, 0))
        
        groups = []
        current_group = [sorted_results[0]]
        
        for result in sorted_results[1:]:
            if self._are_nearby(current_group[-1], result):
                current_group.append(result)
            else:
                groups.append(current_group)
                current_group = [result]
        
        groups.append(current_group)
        return groups    
    def _are_nearby(self, result1: OCRResult, result2: OCRResult, threshold: float = 50) -> bool:
        """Check if two OCR results are spatially nearby"""
        if not result1.bbox or not result2.bbox:
            return False
        
        # Check vertical distance
        y_dist = abs(result1.bbox[1] - result2.bbox[1])
        if y_dist > threshold:
            return False
        
        # Check horizontal distance
        x_dist = abs(result1.bbox[0] - result2.bbox[0])
        return x_dist < threshold * 3  # Allow more horizontal spacing

# FastAPI application
app = FastAPI(title="OCR Ensemble API", version="1.0.0")
ocr_engine = OCREngine()

class OCRRequest(BaseModel):
    image_path: str
    enable_preprocessing: bool = True

class OCRResponse(BaseModel):
    text: str
    confidence: float
    word_count: int
    processing_time: float

@app.get("/health")
async def health_check():
    return {"status": "healthy", "gpu_available": torch.cuda.is_available()}

@app.post("/process", response_model=OCRResponse)
async def process_image(request: OCRRequest):
    """Process an image with ensemble OCR"""
    try:
        image_path = Path(request.image_path)
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image file not found")
        
        ocr_engine.preprocessing_enabled = request.enable_preprocessing
        result = await ocr_engine.process_image(image_path)
        
        return OCRResponse(
            text=result["text"],
            confidence=result["average_confidence"],
            word_count=result["word_count"],
            processing_time=result["processing_time"]
        )
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/batch")
async def batch_process(files: List[UploadFile] = File(...)):
    """Process multiple images in batch"""
    results = []
    for file in files:
        temp_path = Path(f"/tmp/{file.filename}")
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        result = await ocr_engine.process_image(temp_path)
        results.append({
            "filename": file.filename,
            **result
        })
        
        temp_path.unlink()
    
    return {"results": results, "total_files": len(files)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)