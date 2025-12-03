"""
Visual Analysis Module - Screenshots and Visual Comparison
Professional implementation using Playwright
"""
from typing import Dict, Optional, Tuple
import base64
import io
from PIL import Image
import time


class VisualAnalyzer:
    """
    Visual analysis:
    - Screenshot capture
    - Mobile vs desktop comparison
    - Visual hierarchy analysis
    - Color analysis
    """
    
    def __init__(self):
        self.browser = None
        self.playwright_available = False
        self._init_playwright()
    
    def _init_playwright(self):
        """Initialize Playwright if available"""
        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright
            self.playwright_available = True
        except ImportError:
            self.playwright_available = False
            print("Playwright not available. Install with: pip install playwright && playwright install")
    
    def capture_screenshot(self, url: str, viewport: Dict = None, wait_time: int = 3000) -> Optional[Dict]:
        """
        Capture screenshot of URL
        
        Args:
            url: URL to capture
            viewport: Viewport size {'width': 1920, 'height': 1080}
            wait_time: Time to wait before screenshot (ms)
            
        Returns:
            Dictionary with screenshot data
        """
        if not self.playwright_available:
            return {
                'error': 'Playwright not available',
                'has_error': True
            }
        
        try:
            with self.playwright().start() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport=viewport or {'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Navigate and wait
                page.goto(url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(wait_time)
                
                # Capture screenshot
                screenshot_bytes = page.screenshot(full_page=True)
                
                # Convert to base64
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                # Get page dimensions
                dimensions = page.evaluate('''() => {
                    return {
                        width: document.documentElement.scrollWidth,
                        height: document.documentElement.scrollHeight,
                        viewport_width: window.innerWidth,
                        viewport_height: window.innerHeight
                    };
                }''')
                
                browser.close()
                
                return {
                    'screenshot': screenshot_b64,
                    'dimensions': dimensions,
                    'has_error': False
                }
                
        except Exception as e:
            return {
                'error': f'Screenshot capture failed: {str(e)}',
                'has_error': True
            }
    
    def capture_mobile_screenshot(self, url: str) -> Optional[Dict]:
        """Capture mobile screenshot"""
        mobile_viewport = {
            'width': 375,
            'height': 667,
            'device_scale_factor': 2
        }
        return self.capture_screenshot(url, mobile_viewport)
    
    def capture_desktop_screenshot(self, url: str) -> Optional[Dict]:
        """Capture desktop screenshot"""
        desktop_viewport = {
            'width': 1920,
            'height': 1080
        }
        return self.capture_screenshot(url, desktop_viewport)
    
    def analyze_visual_hierarchy(self, screenshot_b64: str) -> Dict:
        """
        Analyze visual hierarchy from screenshot
        
        Args:
            screenshot_b64: Base64 encoded screenshot
            
        Returns:
            Dictionary with visual analysis
        """
        try:
            # Decode image
            image_data = base64.b64decode(screenshot_b64)
            image = Image.open(io.BytesIO(image_data))
            
            # Get image stats
            width, height = image.size
            mode = image.mode
            
            # Convert to RGB if needed
            if mode != 'RGB':
                image = image.convert('RGB')
            
            # Analyze colors
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                # Get dominant colors
                colors_sorted = sorted(colors, key=lambda x: x[0], reverse=True)
                dominant_colors = colors_sorted[:5]
                
                # Calculate color distribution
                total_pixels = width * height
                color_distribution = [
                    {
                        'color': f'#{rgb[1]:02x}{rgb[2]:02x}{rgb[3]:02x}' if len(rgb) > 3 else '#000000',
                        'percentage': round((count / total_pixels) * 100, 2)
                    }
                    for count, rgb in dominant_colors
                ]
            else:
                color_distribution = []
            
            return {
                'width': width,
                'height': height,
                'aspect_ratio': round(width / height, 2),
                'total_pixels': total_pixels,
                'dominant_colors': color_distribution,
                'file_size_kb': len(image_data) / 1024
            }
            
        except Exception as e:
            return {
                'error': f'Visual analysis failed: {str(e)}',
                'has_error': True
            }
    
    def compare_screenshots(self, screenshot1: Dict, screenshot2: Dict) -> Dict:
        """
        Compare two screenshots
        
        Args:
            screenshot1: First screenshot data
            screenshot2: Second screenshot data
            
        Returns:
            Comparison results
        """
        try:
            # Decode images
            img1_data = base64.b64decode(screenshot1.get('screenshot', ''))
            img2_data = base64.b64decode(screenshot2.get('screenshot', ''))
            
            img1 = Image.open(io.BytesIO(img1_data))
            img2 = Image.open(io.BytesIO(img2_data))
            
            # Resize if different sizes
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
            
            # Calculate difference
            diff = Image.new('RGB', img1.size)
            pixels1 = img1.load()
            pixels2 = img2.load()
            diff_pixels = diff.load()
            
            total_diff = 0
            for x in range(img1.size[0]):
                for y in range(img1.size[1]):
                    r1, g1, b1 = pixels1[x, y]
                    r2, g2, b2 = pixels2[x, y]
                    
                    # Calculate difference
                    r_diff = abs(r1 - r2)
                    g_diff = abs(g1 - g2)
                    b_diff = abs(b1 - b2)
                    
                    total_diff += (r_diff + g_diff + b_diff) / 3
                    
                    # Set diff pixel
                    diff_pixels[x, y] = (r_diff, g_diff, b_diff)
            
            # Calculate similarity percentage
            max_diff = img1.size[0] * img1.size[1] * 255
            similarity = 100 - ((total_diff / max_diff) * 100)
            
            # Convert diff to base64
            diff_buffer = io.BytesIO()
            diff.save(diff_buffer, format='PNG')
            diff_b64 = base64.b64encode(diff_buffer.getvalue()).decode('utf-8')
            
            return {
                'similarity_percentage': round(similarity, 2),
                'difference_image': diff_b64,
                'has_error': False
            }
            
        except Exception as e:
            return {
                'error': f'Screenshot comparison failed: {str(e)}',
                'has_error': True
            }

