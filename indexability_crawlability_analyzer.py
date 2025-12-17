"""
Indexability & Crawlability Analyzer.

Analyzes:
- Robots.txt rule simulation
- Meta robots conflicts
- X-Robots-Tag header detection
- Canonical chain detection
- Noindex + internal link conflict detection
"""
import requests
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re


class IndexabilityCrawlabilityAnalyzer:
    """
    Analyzes indexability and crawlability issues.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.session = self._create_session()
        self._robots_txt_cache = {}  # Cache robots.txt per domain
    
    def _create_session(self):
        """Create a requests session."""
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
    
    def analyze_page(self, html_content: str, page_url: str, response_headers: Optional[Dict] = None) -> Dict:
        """
        Analyze page for indexability and crawlability.
        
        Args:
            html_content: HTML content of the page
            page_url: URL of the page
            response_headers: Optional HTTP response headers
            
        Returns:
            Dictionary with indexability/crawlability analysis
        """
        soup = BeautifulSoup(html_content, 'lxml')
        parsed_url = urlparse(page_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        results = {
            'robots_txt': self._check_robots_txt(page_url, base_url),
            'meta_robots': self._analyze_meta_robots(soup),
            'x_robots_tag': self._analyze_x_robots_tag(response_headers or {}),
            'canonical': self._analyze_canonical(soup, page_url),
            'noindex_conflicts': [],
            'indexability_status': 'indexable',
            'crawlability_status': 'crawlable',
            'issues': []
        }
        
        # Check for conflicts
        results['noindex_conflicts'] = self._detect_noindex_conflicts(
            results, page_url, html_content
        )
        
        # Determine overall status
        results['indexability_status'] = self._determine_indexability_status(results)
        results['crawlability_status'] = self._determine_crawlability_status(results)
        
        # Collect all issues
        results['issues'] = self._collect_all_issues(results)
        
        return results
    
    def _check_robots_txt(self, page_url: str, base_url: str) -> Dict:
        """
        Check robots.txt rules for this URL.
        
        Returns:
            Dictionary with robots.txt analysis
        """
        parsed_url = urlparse(page_url)
        domain = parsed_url.netloc
        
        # Check cache
        if domain in self._robots_txt_cache:
            robots_content = self._robots_txt_cache[domain]
        else:
            # Fetch robots.txt
            robots_url = urljoin(base_url, '/robots.txt')
            try:
                response = self.session.get(robots_url, timeout=5)
                if response.status_code == 200:
                    robots_content = response.text
                    self._robots_txt_cache[domain] = robots_content
                else:
                    robots_content = None
            except:
                robots_content = None
        
        if not robots_content:
            return {
                'available': False,
                'blocks_page': False,
                'allows_page': True,
                'message': 'robots.txt not accessible or does not exist'
            }
        
        # Parse robots.txt (simplified)
        blocks_user_agent = False
        allows_user_agent = True
        path = parsed_url.path
        
        # Check for User-agent: * rules
        lines = robots_content.split('\n')
        current_user_agent = None
        in_user_agent_block = False
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # User-agent directive
            if line.lower().startswith('user-agent:'):
                ua = line.split(':', 1)[1].strip()
                current_user_agent = ua.lower()
                in_user_agent_block = (current_user_agent == '*' or current_user_agent == 'googlebot')
            
            # Disallow directive
            elif line.lower().startswith('disallow:') and in_user_agent_block:
                pattern = line.split(':', 1)[1].strip()
                if pattern and self._robots_pattern_matches(path, pattern):
                    blocks_user_agent = True
                    allows_user_agent = False
            
            # Allow directive
            elif line.lower().startswith('allow:') and in_user_agent_block:
                pattern = line.split(':', 1)[1].strip()
                if pattern and self._robots_pattern_matches(path, pattern):
                    allows_user_agent = True
                    blocks_user_agent = False
        
        return {
            'available': True,
            'blocks_page': blocks_user_agent,
            'allows_page': allows_user_agent,
            'path_checked': path,
            'message': 'Blocked by robots.txt' if blocks_user_agent else 'Allowed by robots.txt'
        }
    
    @staticmethod
    def _robots_pattern_matches(path: str, pattern: str) -> bool:
        """
        Check if a path matches a robots.txt pattern.
        
        Simplified pattern matching - supports * and $.
        """
        if not pattern:
            return False
        
        # Convert pattern to regex
        pattern = pattern.replace('*', '.*')
        if pattern.endswith('$'):
            pattern = pattern[:-1] + '$'
        else:
            pattern = pattern + '.*'
        
        try:
            return bool(re.match(pattern, path))
        except:
            return False
    
    def _analyze_meta_robots(self, soup: BeautifulSoup) -> Dict:
        """
        Analyze meta robots tags.
        
        Returns:
            Dictionary with meta robots analysis
        """
        meta_robots = soup.find('meta', attrs={'name': re.compile(r'robots', re.I)})
        
        if not meta_robots:
            return {
                'present': False,
                'noindex': False,
                'nofollow': False,
                'noarchive': False,
                'nosnippet': False,
                'content': None
            }
        
        content = meta_robots.get('content', '').lower()
        
        return {
            'present': True,
            'noindex': 'noindex' in content,
            'nofollow': 'nofollow' in content,
            'noarchive': 'noarchive' in content,
            'nosnippet': 'nosnippet' in content,
            'content': content
        }
    
    def _analyze_x_robots_tag(self, headers: Dict) -> Dict:
        """
        Analyze X-Robots-Tag HTTP header.
        
        Args:
            headers: HTTP response headers (dict-like)
            
        Returns:
            Dictionary with X-Robots-Tag analysis
        """
        # Handle both dict and CaseInsensitiveDict
        header_value = None
        for key, value in headers.items():
            if key.lower() == 'x-robots-tag':
                header_value = value
                break
        
        if not header_value:
            return {
                'present': False,
                'noindex': False,
                'nofollow': False,
                'content': None
            }
        
        content_lower = header_value.lower()
        
        return {
            'present': True,
            'noindex': 'noindex' in content_lower,
            'nofollow': 'nofollow' in content_lower,
            'content': header_value
        }
    
    def _analyze_canonical(self, soup: BeautifulSoup, page_url: str) -> Dict:
        """
        Analyze canonical tag and detect canonical chains.
        
        Returns:
            Dictionary with canonical analysis
        """
        canonical_tag = soup.find('link', attrs={'rel': re.compile(r'canonical', re.I)})
        
        if not canonical_tag:
            return {
                'present': False,
                'url': None,
                'is_self_canonical': False,
                'chain_detected': False
            }
        
        canonical_url = canonical_tag.get('href', '')
        
        # Check if it's self-referential
        is_self = canonical_url == page_url or urlparse(canonical_url).path == urlparse(page_url).path
        
        return {
            'present': True,
            'url': canonical_url,
            'is_self_canonical': is_self,
            'chain_detected': False,  # Would need to crawl canonical URL to detect chains
            'issue': None if is_self else f'Canonical points to different URL: {canonical_url}'
        }
    
    def _detect_noindex_conflicts(self, results: Dict, page_url: str, html_content: str) -> List[Dict]:
        """
        Detect conflicts when page is noindex but has internal links.
        
        Note: This will be enhanced during report generation when we have full site context.
        """
        conflicts = []
        
        meta_robots = results.get('meta_robots', {})
        x_robots = results.get('x_robots_tag', {})
        
        is_noindex = meta_robots.get('noindex') or x_robots.get('noindex')
        
        if is_noindex:
            # Check for internal links in HTML
            soup = BeautifulSoup(html_content, 'lxml')
            links = soup.find_all('a', href=True)
            internal_links = []
            
            parsed = urlparse(page_url)
            base_domain = parsed.netloc
            
            for link in links:
                href = link.get('href', '')
                if href:
                    link_parsed = urlparse(urljoin(page_url, href))
                    if link_parsed.netloc == base_domain:
                        internal_links.append(href)
            
            if internal_links:
                conflicts.append({
                    'type': 'noindex_with_internal_links',
                    'issue': f'Page is marked noindex but contains {len(internal_links)} internal links',
                    'internal_links_count': len(internal_links),
                    'recommendation': 'Either remove noindex directive or remove internal links to this page'
                })
        
        return conflicts
    
    def _determine_indexability_status(self, results: Dict) -> str:
        """Determine if page is indexable."""
        robots_txt = results.get('robots_txt', {})
        meta_robots = results.get('meta_robots', {})
        x_robots = results.get('x_robots_tag', {})
        
        # Check robots.txt
        if robots_txt.get('blocks_page'):
            return 'blocked_by_robots_txt'
        
        # Check meta robots or X-Robots-Tag
        if meta_robots.get('noindex') or x_robots.get('noindex'):
            return 'noindex'
        
        return 'indexable'
    
    def _determine_crawlability_status(self, results: Dict) -> str:
        """Determine if page is crawlable."""
        robots_txt = results.get('robots_txt', {})
        meta_robots = results.get('meta_robots', {})
        x_robots = results.get('x_robots_tag', {})
        
        # Check robots.txt
        if robots_txt.get('blocks_page'):
            return 'blocked_by_robots_txt'
        
        # Check nofollow
        if meta_robots.get('nofollow') or x_robots.get('nofollow'):
            return 'nofollow'  # Still crawlable, but links won't be followed
        
        return 'crawlable'
    
    def _collect_all_issues(self, results: Dict) -> List[Dict]:
        """Collect all indexability/crawlability issues."""
        issues = []
        
        # Robots.txt blocking
        if results.get('robots_txt', {}).get('blocks_page'):
            issues.append({
                'type': 'robots_txt_block',
                'severity': 'critical',
                'issue': 'Page is blocked by robots.txt',
                'recommendation': 'Update robots.txt to allow crawling this page'
            })
        
        # Noindex issues
        meta_robots = results.get('meta_robots', {})
        x_robots = results.get('x_robots_tag', {})
        
        if meta_robots.get('noindex') or x_robots.get('noindex'):
            issues.append({
                'type': 'noindex',
                'severity': 'warning',
                'issue': 'Page is marked as noindex',
                'recommendation': 'Remove noindex directive if you want this page indexed'
            })
        
        # Canonical issues
        canonical = results.get('canonical', {})
        if canonical.get('present') and not canonical.get('is_self_canonical'):
            issues.append({
                'type': 'canonical_chain',
                'severity': 'info',
                'issue': f"Canonical points to different URL: {canonical.get('url')}",
                'recommendation': 'Ensure canonical URLs are correct to avoid indexing issues'
            })
        
        # Noindex conflicts
        conflicts = results.get('noindex_conflicts', [])
        issues.extend(conflicts)
        
        return issues

