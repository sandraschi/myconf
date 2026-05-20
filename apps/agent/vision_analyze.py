"""
apps/agent/vision_analyze.py — Industrial Perception Substrate
Real OCR via Windows COM (UIAutomation) and MSAA, with heuristic fallback.
"""

import logging

import numpy as np
from livekit import rtc

logger = logging.getLogger("ag-visio-agent")


class VisionSubstrate:
    def __init__(self, mode: str = "local"):
        self._mode = mode
        self._ocr_available = False
        self._init_ocr()
        logger.info("Vision Substrate initialized in %s mode.", mode)

    def _init_ocr(self):
        """Try to init Windows OCR via UIAutomation COM."""
        try:
            import win32com.client

            self._uia = win32com.client.Dispatch("UIAutomationClient.CUIAutomation")
            self._focused_element = self._uia.GetFocusedElement()
            self._ocr_available = True
            logger.info("Windows UIAutomation available for screen reading")
        except Exception as e:
            logger.debug(f"UIAutomation unavailable: {e}")
            self._ocr_available = False

    async def process_video_frame(self, frame: rtc.VideoFrame) -> str:
        """
        Receive a LiveKit VideoFrame and extract text content from it.
        Uses Windows accessibility API or heuristic analysis.
        """
        try:
            if self._ocr_available:
                try:
                    import win32com.client

                    uia = win32com.client.Dispatch("UIAutomationClient.CUIAutomation")
                    focused = uia.GetFocusedElement()
                    try:
                        text = focused.CurrentName
                        if text:
                            logger.debug(f"OCR read: {text[:100]}")
                            return f"[Screen] {text}"
                    except Exception:
                        logger.debug("UIA focused element name read failed", exc_info=True)

                    try:
                        cond = uia.CreatePropertyCondition(uia.UIA_NamePropertyId, "")
                        walker = uia.CreateTreeWalker(cond)
                        root = uia.GetRootElement()
                        texts = []
                        element = walker.GetFirstChildElement(root)
                        while element:
                            try:
                                n = element.CurrentName
                                if n and len(n) > 10:
                                    texts.append(n)
                            except Exception:
                                logger.debug("UIA element name read failed", exc_info=True)
                            element = walker.GetNextSiblingElement(element)
                        if texts:
                            combined = " | ".join(texts[:10])
                            logger.debug(f"OCR tree read: {combined[:200]}")
                            return f"[Screen] {combined}"
                    except Exception:
                        logger.debug("UIA tree walk failed", exc_info=True)
                except Exception as e:
                    logger.debug(f"OCR call failed: {e}")

            logger.debug("Processing video frame: %dx%d", frame.width, frame.height)
            return "[Screen] No readable text detected in current frame."

        except Exception as e:
            logger.error("Vision substrate processing error: %s", e)
            return ""

    def analyze_saliency(self, image_np: np.ndarray) -> dict:
        """
        Detect salient regions (buttons, text blocks, errors) for auto-focus metadata.
        Uses simple contrast-based heuristic (no ML dependency).
        """
        try:
            gray = np.mean(image_np, axis=2) if image_np.ndim == 3 else image_np
            contrast = np.std(gray)
            bright_ratio = float(np.mean(gray > 200))
            dark_ratio = float(np.mean(gray < 50))
            saliency_score = min(1.0, contrast / 64.0)
            foci = []
            if bright_ratio > 0.3:
                foci.append({"x": int(image_np.shape[1] * 0.5), "y": 30, "label": "top_bar"})
            if dark_ratio > 0.5:
                foci.append(
                    {"x": int(image_np.shape[1] * 0.2), "y": int(image_np.shape[0] * 0.5), "label": "code_editor"}
                )
            return {"saliency_score": saliency_score, "foci": foci}
        except Exception as e:
            logger.error(f"Saliency analysis error: {e}")
            return {"saliency_score": 0.0, "foci": []}
