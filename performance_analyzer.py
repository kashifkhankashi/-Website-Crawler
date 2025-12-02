"""
Performance analyzer for detecting slow-loading elements and performance issues.
"""
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PerformanceAnalyzer:
    """
    Analyzes page performance by detecting:
    - Heavy images
    - Slow JS/CSS files
    - Slow HTML sections
    - Slow components
    """
    
    def __init__(self):
        self.session = self._create_session()
        self.image_size_threshold_kb = 200  # Flag images > 200KB
        self.js_css_size_threshold_kb = 100  # Flag JS/CSS > 100KB
        self.max_nested_depth = 10  # Flag elements with >10 levels of nesting
        self.max_children = 50  # Flag elements with >50 direct children
        
    def _create_session(self):
        """Create a requests session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def analyze_page(self, html_content: str, page_url: str) -> Dict:
        """
        Analyze a page for performance issues.
        
        Args:
            html_content: HTML content of the page
            page_url: Base URL of the page
            
        Returns:
            Dictionary with performance analysis results
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        results = {
            'heavy_images': [],
            'slow_js_css': [],
            'slow_html_sections': [],
            'slow_components': [],
            'render_blocking_resources': []
        }
        
        # Analyze images
        results['heavy_images'] = self._analyze_images(soup, page_url)
        
        # Analyze JS/CSS
        js_css_results = self._analyze_js_css(soup, page_url)
        results['slow_js_css'] = js_css_results['files']
        results['render_blocking_resources'] = js_css_results['render_blocking']
        
        # Analyze HTML structure
        results['slow_html_sections'] = self._analyze_html_structure(soup)
        
        # Analyze components
        results['slow_components'] = self._analyze_components(soup, page_url)
        
        return results
    
    def _analyze_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Analyze images for size, resolution, format."""
        heavy_images = []
        
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if not src:
                continue
            
            # Convert to absolute URL
            img_url = urljoin(base_url, src)
            
            # Get image info
            img_info = self._get_image_info(img_url, img)
            if img_info:
                heavy_images.append(img_info)
        
        return heavy_images
    
    def _get_image_info(self, img_url: str, img_tag: Tag) -> Optional[Dict]:
        """Get image information including size."""
        try:
            # Try HEAD request first
            response = self.session.head(img_url, allow_redirects=True, timeout=5)
            content_length = response.headers.get('Content-Length')
            content_type = response.headers.get('Content-Type', '')
            
            size_bytes = None
            if content_length:
                try:
                    size_bytes = int(content_length)
                except ValueError:
                    pass
            
            # If HEAD doesn't work, try GET with range
            if size_bytes is None:
                try:
                    response = self.session.get(
                        img_url, 
                        headers={'Range': 'bytes=0-1023'},
                        timeout=5,
                        stream=True
                    )
                    if 'Content-Range' in response.headers:
                        # Parse Content-Range: bytes 0-1023/1234567
                        range_header = response.headers['Content-Range']
                        match = re.search(r'/(\d+)', range_header)
                        if match:
                            size_bytes = int(match.group(1))
                    elif 'Content-Length' in response.headers:
                        size_bytes = int(response.headers['Content-Length'])
                except:
                    pass
            
            if size_bytes is None:
                return None
            
            size_kb = size_bytes / 1024
            size_mb = size_bytes / (1024 * 1024)
            
            # Get dimensions from attributes
            width = img_tag.get('width')
            height = img_tag.get('height')
            
            # Parse width/height
            try:
                if width:
                    width = int(re.sub(r'[^\d]', '', str(width)))
                if height:
                    height = int(re.sub(r'[^\d]', '', str(height)))
            except:
                width = height = None
            
            # Check if image is heavy
            is_heavy = size_bytes > (self.image_size_threshold_kb * 1024)
            
            # Detect format
            img_format = 'unknown'
            if 'webp' in content_type.lower() or img_url.lower().endswith('.webp'):
                img_format = 'WebP'
            elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower() or img_url.lower().endswith(('.jpg', '.jpeg')):
                img_format = 'JPEG'
            elif 'png' in content_type.lower() or img_url.lower().endswith('.png'):
                img_format = 'PNG'
            elif 'gif' in content_type.lower() or img_url.lower().endswith('.gif'):
                img_format = 'GIF'
            elif 'svg' in content_type.lower() or img_url.lower().endswith('.svg'):
                img_format = 'SVG'
            
            # Get parent element info for location
            parent = img_tag.find_parent(['div', 'section', 'article', 'header', 'footer', 'main', 'aside'])
            location = 'Unknown'
            if parent:
                location = self._get_element_identifier(parent)
            
            result = {
                'url': img_url,
                'size_bytes': size_bytes,
                'size_kb': round(size_kb, 2),
                'size_mb': round(size_mb, 2),
                'width': width,
                'height': height,
                'format': img_format,
                'is_heavy': is_heavy,
                'location': location,
                'alt': img_tag.get('alt', ''),
                'html_snippet': str(img_tag)[:200]  # First 200 chars of HTML
            }
            
            return result if is_heavy else None
            
        except Exception as e:
            # Silently fail for individual images
            return None
    
    def _analyze_js_css(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Analyze JavaScript and CSS files."""
        slow_files = []
        render_blocking = []
        
        # Analyze <script> tags
        for script in soup.find_all('script'):
            src = script.get('src')
            if not src:
                continue
            
            script_url = urljoin(base_url, src)
            is_async = script.get('async') is not None
            is_defer = script.get('defer') is not None
            is_in_head = script.find_parent('head') is not None
            
            # Check if render-blocking
            is_render_blocking = is_in_head and not is_async and not is_defer
            
            file_info = self._get_resource_info(script_url, 'JavaScript')
            if file_info:
                file_info['is_render_blocking'] = is_render_blocking
                file_info['has_async'] = is_async
                file_info['has_defer'] = is_defer
                file_info['in_head'] = is_in_head
                
                if file_info['is_large']:
                    slow_files.append(file_info)
                
                if is_render_blocking:
                    render_blocking.append(file_info)
        
        # Analyze <link> tags for CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if not href:
                continue
            
            css_url = urljoin(base_url, href)
            is_in_head = link.find_parent('head') is not None
            
            # CSS in head is typically render-blocking unless media query excludes it
            media = link.get('media', 'all')
            is_render_blocking = is_in_head and media == 'all'
            
            file_info = self._get_resource_info(css_url, 'CSS')
            if file_info:
                file_info['is_render_blocking'] = is_render_blocking
                file_info['in_head'] = is_in_head
                file_info['media'] = media
                
                if file_info['is_large']:
                    slow_files.append(file_info)
                
                if is_render_blocking:
                    render_blocking.append(file_info)
        
        return {
            'files': slow_files,
            'render_blocking': render_blocking
        }
    
    def _get_resource_info(self, url: str, resource_type: str) -> Optional[Dict]:
        """Get information about a JS/CSS resource."""
        try:
            response = self.session.head(url, allow_redirects=True, timeout=5)
            content_length = response.headers.get('Content-Length')
            
            size_bytes = None
            if content_length:
                try:
                    size_bytes = int(content_length)
                except ValueError:
                    pass
            
            if size_bytes is None:
                return None
            
            size_kb = size_bytes / 1024
            is_large = size_bytes > (self.js_css_size_threshold_kb * 1024)
            
            return {
                'url': url,
                'type': resource_type,
                'size_bytes': size_bytes,
                'size_kb': round(size_kb, 2),
                'is_large': is_large
            }
        except:
            return None
    
    def _analyze_html_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze HTML structure for deeply nested or large sections."""
        slow_sections = []
        
        # Find all major container elements
        containers = soup.find_all(['div', 'section', 'article', 'main', 'header', 'footer', 'aside'])
        
        for container in containers:
            # Count nesting depth
            depth = self._get_nesting_depth(container)
            
            # Count direct children
            children_count = len([c for c in container.children if isinstance(c, Tag)])
            
            # Count images in this section
            images_count = len(container.find_all('img'))
            
            # Check if this section is problematic
            is_problematic = (
                depth > self.max_nested_depth or
                children_count > self.max_children or
                images_count > 10
            )
            
            if is_problematic:
                identifier = self._get_element_identifier(container)
                slow_sections.append({
                    'element': identifier,
                    'tag': container.name,
                    'nesting_depth': depth,
                    'children_count': children_count,
                    'images_count': images_count,
                    'html_snippet': str(container)[:500],  # First 500 chars
                    'issues': self._get_section_issues(depth, children_count, images_count)
                })
        
        return slow_sections
    
    def _get_nesting_depth(self, element: Tag) -> int:
        """Calculate maximum nesting depth of an element."""
        if not element.children:
            return 0
        
        max_depth = 0
        for child in element.children:
            if isinstance(child, Tag):
                depth = 1 + self._get_nesting_depth(child)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _get_element_identifier(self, element: Tag) -> str:
        """Get a human-readable identifier for an element."""
        # Try ID first
        elem_id = element.get('id')
        if elem_id:
            return f"#{elem_id}"
        
        # Try class
        elem_class = element.get('class')
        if elem_class:
            classes = ' '.join(elem_class) if isinstance(elem_class, list) else elem_class
            return f".{classes.split()[0]}" if classes else element.name
        
        # Try data attributes
        for attr in element.attrs:
            if attr.startswith('data-'):
                return f"[{attr}]"
        
        # Fallback to tag name
        return element.name
    
    def _get_section_issues(self, depth: int, children: int, images: int) -> List[str]:
        """Get list of issues for a section."""
        issues = []
        if depth > self.max_nested_depth:
            issues.append(f"Deeply nested ({depth} levels)")
        if children > self.max_children:
            issues.append(f"Too many children ({children} elements)")
        if images > 10:
            issues.append(f"Too many images ({images} images)")
        return issues
    
    def _analyze_components(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Analyze specific components that might be slow."""
        slow_components = []
        
        # Check for carousels/sliders
        carousels = soup.find_all(['div', 'section'], class_=re.compile(r'carousel|slider|swiper', re.I))
        for carousel in carousels:
            images = len(carousel.find_all('img'))
            scripts = len(carousel.find_all('script'))
            if images > 5 or scripts > 0:
                slow_components.append({
                    'type': 'Carousel/Slider',
                    'location': self._get_element_identifier(carousel),
                    'images_count': images,
                    'scripts_count': scripts,
                    'issue': f"Carousel with {images} images may load slowly"
                })
        
        # Check for large tables
        tables = soup.find_all('table')
        for table in tables:
            rows = len(table.find_all('tr'))
            if rows > 100:
                slow_components.append({
                    'type': 'Large Table',
                    'location': self._get_element_identifier(table),
                    'rows_count': rows,
                    'issue': f"Table with {rows} rows may render slowly"
                })
        
        # Check for iframes
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            slow_components.append({
                'type': 'Iframe',
                'location': self._get_element_identifier(iframe),
                'src': src,
                'issue': f"Iframe loading external content: {src[:50]}"
            })
        
        # Check for video elements
        videos = soup.find_all('video')
        for video in videos:
            src = video.get('src', '')
            slow_components.append({
                'type': 'Video',
                'location': self._get_element_identifier(video),
                'src': src,
                'issue': f"Video element may cause slow loading"
            })
        
        return slow_components

