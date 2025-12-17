"""
Security & Trust Signals Analyzer.

Analyzes:
- HTTPS enforcement check
- Mixed content detection
- Missing security headers
- Cookie and consent banner detection
"""
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class SecurityTrustAnalyzer:
    """
    Analyzes security and trust signals.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.security_headers = [
            'Strict-Transport-Security',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Content-Security-Policy',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
    
    def analyze_page(self, html_content: str, page_url: str, response_headers: Optional[Dict] = None) -> Dict:
        """
        Analyze page for security and trust issues.
        
        Args:
            html_content: HTML content of the page
            page_url: URL of the page
            response_headers: Optional HTTP response headers
            
        Returns:
            Dictionary with security/trust analysis
        """
        soup = BeautifulSoup(html_content, 'lxml')
        headers = response_headers or {}
        
        results = {
            'https_enforcement': self._check_https_enforcement(page_url),
            'mixed_content': self._detect_mixed_content(soup, page_url),
            'security_headers': self._analyze_security_headers(headers),
            'cookie_consent': self._detect_cookie_consent(soup),
            'overall_security_score': 'good',
            'issues': []
        }
        
        # Collect all issues
        results['issues'] = self._collect_all_issues(results)
        
        # Calculate overall score
        results['overall_security_score'] = self._calculate_security_score(results)
        
        return results
    
    def _check_https_enforcement(self, page_url: str) -> Dict:
        """Check HTTPS enforcement."""
        parsed = urlparse(page_url)
        is_https = parsed.scheme == 'https'
        
        return {
            'is_https': is_https,
            'is_http': parsed.scheme == 'http',
            'has_issue': not is_https,
            'issue': 'Page is not served over HTTPS' if not is_https else None,
            'recommendation': 'Enable HTTPS and redirect HTTP to HTTPS' if not is_https else None
        }
    
    def _detect_mixed_content(self, soup: BeautifulSoup, page_url: str) -> Dict:
        """
        Detect mixed content (HTTP resources on HTTPS page).
        
        Returns:
            Dictionary with mixed content analysis
        """
        parsed = urlparse(page_url)
        is_https_page = parsed.scheme == 'https'
        
        if not is_https_page:
            return {
                'has_mixed_content': False,
                'http_resources': [],
                'count': 0
            }
        
        http_resources = []
        
        # Check images
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src', '')
            if src and src.startswith('http://'):
                http_resources.append({
                    'type': 'image',
                    'url': src,
                    'element': 'img'
                })
        
        # Check scripts
        for script in soup.find_all('script', src=True):
            src = script.get('src', '')
            if src and src.startswith('http://'):
                http_resources.append({
                    'type': 'javascript',
                    'url': src,
                    'element': 'script'
                })
        
        # Check stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href and href.startswith('http://'):
                http_resources.append({
                    'type': 'stylesheet',
                    'url': href,
                    'element': 'link'
                })
        
        # Check iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if src and src.startswith('http://'):
                http_resources.append({
                    'type': 'iframe',
                    'url': src,
                    'element': 'iframe'
                })
        
        # Check CSS background images (in style attributes and style tags)
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            http_urls = re.findall(r'url\(["\']?(http://[^"\'()]+)["\']?\)', style, re.IGNORECASE)
            for url in http_urls:
                http_resources.append({
                    'type': 'css_background',
                    'url': url,
                    'element': element.name
                })
        
        # Check style tags
        for style_tag in soup.find_all('style'):
            style_content = style_tag.string or ''
            http_urls = re.findall(r'url\(["\']?(http://[^"\'()]+)["\']?\)', style_content, re.IGNORECASE)
            for url in http_urls:
                http_resources.append({
                    'type': 'css_background',
                    'url': url,
                    'element': 'style'
                })
        
        return {
            'has_mixed_content': len(http_resources) > 0,
            'http_resources': http_resources,
            'count': len(http_resources),
            'severity': 'critical' if len(http_resources) > 0 else None,
            'recommendation': 'Update all HTTP resources to HTTPS or use protocol-relative URLs' if http_resources else None
        }
    
    def _analyze_security_headers(self, headers: Dict) -> Dict:
        """
        Analyze security headers.
        
        Args:
            headers: HTTP response headers (dict-like)
            
        Returns:
            Dictionary with security headers analysis
        """
        present_headers = {}
        missing_headers = []
        
        # Handle case-insensitive header lookup
        header_dict = {k.lower(): v for k, v in headers.items()}
        
        for header in self.security_headers:
            header_lower = header.lower()
            if header_lower in header_dict:
                present_headers[header] = header_dict[header_lower]
            else:
                missing_headers.append(header)
        
        # Analyze specific header values
        issues = []
        
        # HSTS
        hsts = present_headers.get('Strict-Transport-Security', '')
        if hsts:
            if 'max-age=0' in hsts.lower():
                issues.append({
                    'header': 'Strict-Transport-Security',
                    'issue': 'HSTS max-age is 0, disabling HTTPS enforcement',
                    'recommendation': 'Set max-age to at least 31536000 (1 year)'
                })
        else:
            issues.append({
                'header': 'Strict-Transport-Security',
                'issue': 'Missing HSTS header',
                'recommendation': 'Add Strict-Transport-Security header to enforce HTTPS'
            })
        
        # X-Frame-Options
        xfo = present_headers.get('X-Frame-Options', '')
        if not xfo:
            issues.append({
                'header': 'X-Frame-Options',
                'issue': 'Missing X-Frame-Options header',
                'recommendation': 'Add X-Frame-Options: DENY or SAMEORIGIN to prevent clickjacking'
            })
        
        # Content-Security-Policy
        csp = present_headers.get('Content-Security-Policy', '')
        if not csp:
            issues.append({
                'header': 'Content-Security-Policy',
                'issue': 'Missing Content-Security-Policy header',
                'recommendation': 'Add CSP header to mitigate XSS attacks'
            })
        
        return {
            'present': present_headers,
            'missing': missing_headers,
            'present_count': len(present_headers),
            'missing_count': len(missing_headers),
            'issues': issues,
            'score': self._calculate_headers_score(len(present_headers), len(self.security_headers))
        }
    
    def _detect_cookie_consent(self, soup: BeautifulSoup) -> Dict:
        """
        Detect cookie consent banners (common patterns).
        
        Returns:
            Dictionary with cookie consent detection
        """
        # Common patterns for cookie consent
        consent_patterns = [
            re.compile(r'cookie.*consent', re.IGNORECASE),
            re.compile(r'accept.*cookie', re.IGNORECASE),
            re.compile(r'gdpr', re.IGNORECASE),
            re.compile(r'privacy.*policy', re.IGNORECASE),
            re.compile(r'cookie.*policy', re.IGNORECASE)
        ]
        
        # Common class/id patterns
        consent_selectors = [
            'cookie',
            'consent',
            'gdpr',
            'privacy-banner',
            'cookie-banner'
        ]
        
        text_content = soup.get_text().lower()
        found_patterns = []
        
        for pattern in consent_patterns:
            if pattern.search(text_content):
                found_patterns.append(pattern.pattern)
        
        # Check for common consent banner elements
        found_elements = []
        for selector in consent_selectors:
            elements = soup.find_all(class_=re.compile(selector, re.I))
            elements.extend(soup.find_all(id=re.compile(selector, re.I)))
            if elements:
                found_elements.extend([e.name for e in elements[:3]])  # Limit to 3
        
        has_consent_banner = len(found_patterns) > 0 or len(found_elements) > 0
        
        return {
            'detected': has_consent_banner,
            'patterns_found': found_patterns,
            'elements_found': list(set(found_elements)),
            'confidence': 'high' if len(found_patterns) >= 2 else 'medium' if has_consent_banner else 'low'
        }
    
    def _collect_all_issues(self, results: Dict) -> List[Dict]:
        """Collect all security/trust issues."""
        issues = []
        
        # HTTPS enforcement
        if results.get('https_enforcement', {}).get('has_issue'):
            issues.append({
                'type': 'no_https',
                'severity': 'critical',
                **results['https_enforcement']
            })
        
        # Mixed content
        mixed_content = results.get('mixed_content', {})
        if mixed_content.get('has_mixed_content'):
            issues.append({
                'type': 'mixed_content',
                'severity': mixed_content.get('severity', 'critical'),
                'count': mixed_content.get('count', 0),
                **mixed_content
            })
        
        # Security headers
        security_headers = results.get('security_headers', {})
        issues.extend(security_headers.get('issues', []))
        
        return issues
    
    @staticmethod
    def _calculate_headers_score(present: int, total: int) -> str:
        """Calculate security headers score."""
        if total == 0:
            return 'unknown'
        
        percentage = (present / total) * 100
        
        if percentage >= 80:
            return 'good'
        elif percentage >= 50:
            return 'needs-improvement'
        else:
            return 'poor'
    
    @staticmethod
    def _calculate_security_score(results: Dict) -> str:
        """Calculate overall security score."""
        issues = results.get('issues', [])
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        
        if len(critical_issues) > 0:
            return 'poor'
        elif len(issues) > 3:
            return 'needs-improvement'
        else:
            return 'good'

