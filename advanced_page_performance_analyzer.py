"""
Advanced Page Performance Analyzer.

Analyzes:
- HTML size per page
- DOM node count
- Total request count
- JS execution time approximation
- CSS file weight analysis
- Font loading analysis
- Third-party script impact report
"""
import re
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AdvancedPagePerformanceAnalyzer:
    """
    Advanced performance analysis beyond basic metrics.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.session = self._create_session()
        
    def _create_session(self):
        """Create a requests session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=1,
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
        Analyze page performance metrics.
        
        Args:
            html_content: HTML content of the page
            page_url: Base URL of the page
            
        Returns:
            Dictionary with performance metrics
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        results = {
            'html_size_bytes': len(html_content.encode('utf-8')),
            'html_size_kb': round(len(html_content.encode('utf-8')) / 1024, 2),
            'dom_node_count': self._count_dom_nodes(soup),
            'total_requests': self._count_total_requests(soup, page_url),
            'js_analysis': self._analyze_javascript(soup, page_url),
            'css_analysis': self._analyze_css(soup, page_url),
            'font_analysis': self._analyze_fonts(soup, page_url),
            'third_party_scripts': self._analyze_third_party_scripts(soup, page_url),
            'resource_summary': {}
        }
        
        # Generate resource summary
        results['resource_summary'] = self._generate_resource_summary(results)
        
        return results
    
    def _count_dom_nodes(self, soup: BeautifulSoup) -> int:
        """Count total DOM nodes in the page."""
        return len(soup.find_all())
    
    def _count_total_requests(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """
        Count total requests the page would make.
        
        Returns:
            Dictionary with request counts by type
        """
        requests_count = {
            'total': 0,
            'images': 0,
            'scripts': 0,
            'stylesheets': 0,
            'fonts': 0,
            'xhr': 0,  # Estimated based on script patterns
            'other': 0
        }
        
        # Count images
        images = soup.find_all('img')
        requests_count['images'] = len([img for img in images if img.get('src') or img.get('data-src')])
        requests_count['total'] += requests_count['images']
        
        # Count scripts
        scripts = soup.find_all('script', src=True)
        requests_count['scripts'] = len(scripts)
        requests_count['total'] += requests_count['scripts']
        
        # Count stylesheets
        stylesheets = soup.find_all('link', rel='stylesheet')
        requests_count['stylesheets'] = len(stylesheets)
        requests_count['total'] += requests_count['stylesheets']
        
        # Count font requests (from @font-face or link rel="preload" as="font")
        font_links = soup.find_all('link', rel=lambda x: x and ('preload' in x.lower() or 'stylesheet' in x.lower()))
        for link in font_links:
            href = link.get('href', '')
            as_attr = link.get('as', '')
            if 'font' in as_attr.lower() or '.woff' in href.lower() or '.woff2' in href.lower() or '.ttf' in href.lower():
                requests_count['fonts'] += 1
                requests_count['total'] += 1
        
        # Estimate XHR requests (can't detect all, but can look for fetch/axios patterns)
        inline_scripts = soup.find_all('script', src=False)
        xhr_patterns = re.compile(r'(fetch|XMLHttpRequest|axios|\.ajax)', re.IGNORECASE)
        for script in inline_scripts:
            script_content = script.string or ''
            if xhr_patterns.search(script_content):
                requests_count['xhr'] += 1  # Estimate
        
        requests_count['total'] += requests_count['xhr']
        
        return requests_count
    
    def _analyze_javascript(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """
        Analyze JavaScript files.
        
        Returns:
            Dictionary with JS analysis results
        """
        js_files = []
        inline_js_count = 0
        total_js_size = 0
        js_execution_time_estimate = 0
        
        # External JS files
        external_scripts = soup.find_all('script', src=True)
        for script in external_scripts:
            src = script.get('src', '')
            if src:
                js_url = urljoin(base_url, src)
                js_info = self._get_resource_info(js_url, 'javascript')
                if js_info:
                    js_files.append(js_info)
                    total_js_size += js_info.get('size_bytes', 0)
                    # Estimate execution time: ~1ms per 10KB (rough estimate)
                    js_execution_time_estimate += (js_info.get('size_bytes', 0) / 10240)
        
        # Inline JS
        inline_scripts = soup.find_all('script', src=False)
        inline_js_count = len(inline_scripts)
        for script in inline_scripts:
            script_content = script.string or ''
            if script_content:
                size = len(script_content.encode('utf-8'))
                total_js_size += size
                js_execution_time_estimate += (size / 10240)
        
        # Check for async/defer attributes
        async_count = len([s for s in external_scripts if s.get('async')])
        defer_count = len([s for s in external_scripts if s.get('defer')])
        
        return {
            'external_files': js_files,
            'external_file_count': len(js_files),
            'inline_script_count': inline_js_count,
            'total_size_bytes': total_js_size,
            'total_size_kb': round(total_js_size / 1024, 2),
            'estimated_execution_time_ms': round(js_execution_time_estimate, 2),
            'async_count': async_count,
            'defer_count': defer_count,
            'blocking_count': len(external_scripts) - async_count - defer_count,
            'issues': self._detect_js_issues(js_files, inline_js_count, async_count, defer_count, len(external_scripts))
        }
    
    def _analyze_css(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """
        Analyze CSS files.
        
        Returns:
            Dictionary with CSS analysis results
        """
        css_files = []
        inline_css_count = 0
        total_css_size = 0
        
        # External CSS files
        external_stylesheets = soup.find_all('link', rel='stylesheet')
        for link in external_stylesheets:
            href = link.get('href', '')
            if href:
                css_url = urljoin(base_url, href)
                css_info = self._get_resource_info(css_url, 'css')
                if css_info:
                    css_files.append(css_info)
                    total_css_size += css_info.get('size_bytes', 0)
        
        # Inline CSS
        inline_styles = soup.find_all('style')
        inline_css_count = len(inline_styles)
        for style in inline_styles:
            style_content = style.string or ''
            if style_content:
                total_css_size += len(style_content.encode('utf-8'))
        
        # Check for media attributes (can indicate non-critical CSS)
        media_queries = [link.get('media', '') for link in external_stylesheets if link.get('media')]
        
        return {
            'external_files': css_files,
            'external_file_count': len(css_files),
            'inline_style_count': inline_css_count,
            'total_size_bytes': total_css_size,
            'total_size_kb': round(total_css_size / 1024, 2),
            'media_queries_count': len(media_queries),
            'issues': self._detect_css_issues(css_files, total_css_size)
        }
    
    def _analyze_fonts(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """
        Analyze font loading.
        
        Returns:
            Dictionary with font analysis results
        """
        font_files = []
        font_faces = []
        total_font_size = 0
        
        # Find @font-face declarations in style tags
        style_tags = soup.find_all('style')
        for style in style_tags:
            style_content = style.string or ''
            if style_content:
                # Extract font-face URLs
                font_face_pattern = re.compile(r'@font-face\s*\{[^}]*url\s*\(["\']?([^"\')]+)["\']?\)', re.IGNORECASE)
                matches = font_face_pattern.findall(style_content)
                for match in matches:
                    font_url = urljoin(base_url, match)
                    font_info = self._get_resource_info(font_url, 'font')
                    if font_info:
                        font_files.append(font_info)
                        total_font_size += font_info.get('size_bytes', 0)
                
                # Check for font-display property
                if '@font-face' in style_content:
                    if 'font-display' not in style_content:
                        font_faces.append({
                            'issue': 'Missing font-display property',
                            'recommendation': 'Add font-display: swap or optional to prevent FOIT/FOUT'
                        })
        
        # Find font preloads
        font_preloads = soup.find_all('link', rel='preload', as_='font')
        for preload in font_preloads:
            href = preload.get('href', '')
            if href:
                font_url = urljoin(base_url, href)
                font_info = self._get_resource_info(font_url, 'font')
                if font_info:
                    font_files.append(font_info)
                    total_font_size += font_info.get('size_bytes', 0)
        
        return {
            'font_files': font_files,
            'font_file_count': len(font_files),
            'total_size_bytes': total_font_size,
            'total_size_kb': round(total_font_size / 1024, 2),
            'font_face_issues': font_faces,
            'issues': self._detect_font_issues(font_files, font_faces)
        }
    
    def _analyze_third_party_scripts(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """
        Analyze third-party scripts and their impact.
        
        Returns:
            Dictionary with third-party script analysis
        """
        third_party_scripts = []
        base_domain = urlparse(base_url).netloc
        
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '')
            if src:
                script_url = urljoin(base_url, src)
                script_domain = urlparse(script_url).netloc
                
                # Check if it's third-party (different domain)
                if script_domain and script_domain != base_domain:
                    script_info = {
                        'url': script_url,
                        'domain': script_domain,
                        'async': script.get('async') is not None,
                        'defer': script.get('defer') is not None,
                        'blocking': script.get('async') is None and script.get('defer') is None
                    }
                    
                    # Identify common third-party services
                    script_info['service'] = self._identify_third_party_service(script_url)
                    
                    resource_info = self._get_resource_info(script_url, 'javascript')
                    if resource_info:
                        script_info.update(resource_info)
                    
                    third_party_scripts.append(script_info)
        
        return {
            'scripts': third_party_scripts,
            'count': len(third_party_scripts),
            'blocking_count': len([s for s in third_party_scripts if s.get('blocking')]),
            'domains': list(set([s['domain'] for s in third_party_scripts])),
            'issues': self._detect_third_party_issues(third_party_scripts)
        }
    
    def _get_resource_info(self, url: str, resource_type: str) -> Optional[Dict]:
        """
        Get information about a resource (size, etc.).
        
        Args:
            url: Resource URL
            resource_type: Type of resource ('javascript', 'css', 'font', etc.)
            
        Returns:
            Dictionary with resource info or None if unavailable
        """
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            size = response.headers.get('Content-Length')
            if size:
                size_bytes = int(size)
                return {
                    'url': url,
                    'size_bytes': size_bytes,
                    'size_kb': round(size_bytes / 1024, 2),
                    'size_mb': round(size_bytes / (1024 * 1024), 2),
                    'content_type': response.headers.get('Content-Type', ''),
                    'cache_control': response.headers.get('Cache-Control', ''),
                    'status_code': response.status_code
                }
        except:
            pass
        
        return {
            'url': url,
            'size_bytes': None,
            'error': 'Could not fetch resource info'
        }
    
    def _identify_third_party_service(self, url: str) -> Optional[str]:
        """Identify common third-party services from URL."""
        url_lower = url.lower()
        service_patterns = {
            'Google Analytics': ['google-analytics', 'googletagmanager', 'gtag'],
            'Google Tag Manager': ['googletagmanager.com'],
            'Facebook Pixel': ['facebook.net', 'facebook.com/tr'],
            'Hotjar': ['hotjar.com'],
            'Mixpanel': ['mixpanel.com'],
            'Segment': ['segment.io', 'segment.com'],
            'Amplitude': ['amplitude.com'],
            'Disqus': ['disqus.com'],
            'YouTube': ['youtube.com', 'ytimg.com'],
            'Vimeo': ['vimeo.com'],
            'Stripe': ['stripe.com'],
            'PayPal': ['paypal.com'],
            'Twitter': ['twitter.com', 'twimg.com'],
            'LinkedIn': ['linkedin.com'],
            'Instagram': ['instagram.com'],
            'Cloudflare': ['cloudflare.com'],
            'CDN': ['cdn', 'jsdelivr', 'unpkg', 'cdnjs']
        }
        
        for service, patterns in service_patterns.items():
            if any(pattern in url_lower for pattern in patterns):
                return service
        
        return 'Unknown'
    
    def _detect_js_issues(self, js_files: List[Dict], inline_count: int, async_count: int, defer_count: int, total_external: int) -> List[Dict]:
        """Detect JavaScript-related issues."""
        issues = []
        
        # Large JS files
        for js_file in js_files:
            size_kb = js_file.get('size_kb', 0)
            if size_kb > 500:
                issues.append({
                    'type': 'large_js_file',
                    'file': js_file.get('url', ''),
                    'size_kb': size_kb,
                    'severity': 'warning',
                    'recommendation': f'Consider code splitting or minification. File is {size_kb:.1f}KB'
                })
        
        # Blocking scripts
        blocking_count = total_external - async_count - defer_count
        if blocking_count > 5:
            issues.append({
                'type': 'too_many_blocking_scripts',
                'count': blocking_count,
                'severity': 'warning',
                'recommendation': f'Consider using async or defer for {blocking_count} scripts to improve page load'
            })
        
        # Too many inline scripts
        if inline_count > 10:
            issues.append({
                'type': 'too_many_inline_scripts',
                'count': inline_count,
                'severity': 'info',
                'recommendation': 'Consider moving inline scripts to external files for better caching'
            })
        
        return issues
    
    def _detect_css_issues(self, css_files: List[Dict], total_size: int) -> List[Dict]:
        """Detect CSS-related issues."""
        issues = []
        
        # Large CSS files
        for css_file in css_files:
            size_kb = css_file.get('size_kb', 0)
            if size_kb > 200:
                issues.append({
                    'type': 'large_css_file',
                    'file': css_file.get('url', ''),
                    'size_kb': size_kb,
                    'severity': 'warning',
                    'recommendation': f'Consider splitting CSS or removing unused styles. File is {size_kb:.1f}KB'
                })
        
        # Very large total CSS
        total_kb = round(total_size / 1024, 2)
        if total_kb > 500:
            issues.append({
                'type': 'large_total_css',
                'total_kb': total_kb,
                'severity': 'warning',
                'recommendation': f'Total CSS is {total_kb:.1f}KB. Consider critical CSS extraction and lazy loading'
            })
        
        return issues
    
    def _detect_font_issues(self, font_files: List[Dict], font_faces: List[Dict]) -> List[Dict]:
        """Detect font-related issues."""
        issues = font_faces.copy()  # Copy font-display issues
        
        # Large font files
        for font_file in font_files:
            size_kb = font_file.get('size_kb', 0)
            if size_kb > 200:
                issues.append({
                    'type': 'large_font_file',
                    'file': font_file.get('url', ''),
                    'size_kb': size_kb,
                    'severity': 'warning',
                    'recommendation': f'Consider font subsetting or using system fonts. File is {size_kb:.1f}KB'
                })
        
        # Too many fonts
        if len(font_files) > 5:
            issues.append({
                'type': 'too_many_fonts',
                'count': len(font_files),
                'severity': 'info',
                'recommendation': f'Loading {len(font_files)} fonts may impact performance. Consider reducing font variety'
            })
        
        return issues
    
    def _detect_third_party_issues(self, third_party_scripts: List[Dict]) -> List[Dict]:
        """Detect third-party script issues."""
        issues = []
        
        # Blocking third-party scripts
        blocking = [s for s in third_party_scripts if s.get('blocking')]
        if blocking:
            issues.append({
                'type': 'blocking_third_party_scripts',
                'count': len(blocking),
                'scripts': [s['url'] for s in blocking[:5]],  # Limit to first 5
                'severity': 'warning',
                'recommendation': f'{len(blocking)} third-party scripts are blocking page load. Consider async/defer'
            })
        
        # Too many third-party scripts
        if len(third_party_scripts) > 10:
            issues.append({
                'type': 'too_many_third_party_scripts',
                'count': len(third_party_scripts),
                'severity': 'warning',
                'recommendation': f'{len(third_party_scripts)} third-party scripts may significantly impact performance'
            })
        
        return issues
    
    def _generate_resource_summary(self, results: Dict) -> Dict:
        """Generate summary of all resources."""
        total_size = results.get('html_size_bytes', 0)
        
        js_analysis = results.get('js_analysis', {})
        css_analysis = results.get('css_analysis', {})
        font_analysis = results.get('font_analysis', {})
        
        total_size += js_analysis.get('total_size_bytes', 0)
        total_size += css_analysis.get('total_size_bytes', 0)
        total_size += font_analysis.get('total_size_bytes', 0)
        
        return {
            'total_page_size_bytes': total_size,
            'total_page_size_kb': round(total_size / 1024, 2),
            'total_page_size_mb': round(total_size / (1024 * 1024), 2),
            'html_percentage': round((results.get('html_size_bytes', 0) / total_size * 100) if total_size > 0 else 0, 2),
            'js_percentage': round((js_analysis.get('total_size_bytes', 0) / total_size * 100) if total_size > 0 else 0, 2),
            'css_percentage': round((css_analysis.get('total_size_bytes', 0) / total_size * 100) if total_size > 0 else 0, 2),
            'font_percentage': round((font_analysis.get('total_size_bytes', 0) / total_size * 100) if total_size > 0 else 0, 2)
        }

