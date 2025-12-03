"""
Advanced Link Analysis Module
Professional implementation for internal/external link analysis
"""
from typing import Dict, List, Set, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import defaultdict, Counter
import re


class LinkAnalyzer:
    """
    Advanced link analysis:
    - Internal link graph
    - Anchor text analysis
    - Link equity flow
    - Orphan page detection
    - Deep link analysis
    """
    
    def __init__(self):
        self.internal_links = defaultdict(list)
        self.external_links = defaultdict(list)
        self.anchor_texts = defaultdict(list)
        self.link_counts = defaultdict(int)
        self.domain = None
    
    def analyze_links(self, soup: BeautifulSoup, url: str, all_pages: List[Dict] = None) -> Dict:
        """
        Comprehensive link analysis
        
        Args:
            soup: BeautifulSoup object
            url: Current page URL
            all_pages: List of all crawled pages (for site-wide analysis)
            
        Returns:
            Dictionary with link analysis results
        """
        parsed = urlparse(url)
        self.domain = parsed.netloc
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        anchor_texts = []
        nofollow_links = []
        follow_links = []
        
        for link in links:
            href = link.get('href', '').strip()
            if not href or href.startswith('#'):
                continue
            
            # Get anchor text
            anchor_text = link.get_text(strip=True)
            if anchor_text:
                anchor_texts.append(anchor_text)
            
            # Check rel attributes
            rel = link.get('rel', [])
            is_nofollow = 'nofollow' in [r.lower() for r in rel] if isinstance(rel, list) else 'nofollow' in str(rel).lower()
            is_sponsored = 'sponsored' in [r.lower() for r in rel] if isinstance(rel, list) else 'sponsored' in str(rel).lower()
            is_ugc = 'ugc' in [r.lower() for r in rel] if isinstance(rel, list) else 'ugc' in str(rel).lower()
            
            # Resolve URL
            if href.startswith('http'):
                link_url = href
            elif href.startswith('/'):
                link_url = urljoin(url, href)
            else:
                link_url = urljoin(url, href)
            
            try:
                link_parsed = urlparse(link_url)
                link_domain = link_parsed.netloc
                
                if link_domain == self.domain:
                    internal_links.append({
                        'url': link_url,
                        'anchor_text': anchor_text,
                        'nofollow': is_nofollow,
                        'sponsored': is_sponsored,
                        'ugc': is_ugc
                    })
                else:
                    external_links.append({
                        'url': link_url,
                        'domain': link_domain,
                        'anchor_text': anchor_text,
                        'nofollow': is_nofollow,
                        'sponsored': is_sponsored,
                        'ugc': is_ugc
                    })
                    
                if is_nofollow:
                    nofollow_links.append(link_url)
                else:
                    follow_links.append(link_url)
                    
            except Exception:
                continue
        
        # Analyze anchor texts
        anchor_analysis = self._analyze_anchor_texts(anchor_texts)
        
        # Calculate link metrics
        link_metrics = {
            'total_links': len(links),
            'internal_links_count': len(internal_links),
            'external_links_count': len(external_links),
            'nofollow_count': len(nofollow_links),
            'follow_count': len(follow_links),
            'nofollow_ratio': len(nofollow_links) / len(links) if links else 0,
            'external_domains': len(set([link['domain'] for link in external_links if 'domain' in link]))
        }
        
        # Site-wide analysis if all_pages provided
        site_analysis = None
        if all_pages:
            site_analysis = self._analyze_site_links(all_pages, url)
        
        return {
            'internal_links': internal_links,
            'external_links': external_links,
            'anchor_texts': anchor_texts,
            'anchor_analysis': anchor_analysis,
            'link_metrics': link_metrics,
            'site_analysis': site_analysis
        }
    
    def _analyze_anchor_texts(self, anchor_texts: List[str]) -> Dict:
        """Analyze anchor text patterns"""
        if not anchor_texts:
            return {
                'total': 0,
                'unique': 0,
                'keyword_rich': 0,
                'branded': 0,
                'generic': 0,
                'empty': 0,
                'top_anchors': []
            }
        
        keyword_rich = 0
        branded = 0
        generic = 0
        empty = 0
        
        # Common generic anchor texts
        generic_anchors = {
            'click here', 'read more', 'learn more', 'here', 'this', 'link',
            'more', 'continue', 'next', 'previous', 'view', 'see', 'go'
        }
        
        # Brand indicators
        brand_indicators = ['home', 'homepage', 'logo', 'brand', 'company']
        
        anchor_counter = Counter()
        
        for anchor in anchor_texts:
            anchor_lower = anchor.lower().strip()
            anchor_counter[anchor_lower] += 1
            
            if not anchor_lower or anchor_lower in ['', ' ']:
                empty += 1
            elif anchor_lower in generic_anchors:
                generic += 1
            elif any(indicator in anchor_lower for indicator in brand_indicators):
                branded += 1
            elif len(anchor_lower.split()) >= 2:  # Multi-word likely keyword-rich
                keyword_rich += 1
            else:
                # Single word, check if it's a keyword
                if len(anchor_lower) > 4:  # Longer words more likely to be keywords
                    keyword_rich += 1
                else:
                    generic += 1
        
        return {
            'total': len(anchor_texts),
            'unique': len(set(anchor_texts)),
            'keyword_rich': keyword_rich,
            'branded': branded,
            'generic': generic,
            'empty': empty,
            'keyword_rich_ratio': keyword_rich / len(anchor_texts) if anchor_texts else 0,
            'top_anchors': anchor_counter.most_common(20)
        }
    
    def _analyze_site_links(self, all_pages: List[Dict], current_url: str) -> Dict:
        """Analyze site-wide link structure"""
        # Build link graph
        link_graph = defaultdict(set)
        incoming_links = defaultdict(int)
        outgoing_links = defaultdict(int)
        
        for page in all_pages:
            page_url = page.get('url', '')
            internal_links = page.get('link_analysis', {}).get('internal_links', [])
            
            for link in internal_links:
                link_url = link.get('url', '')
                if link_url:
                    link_graph[page_url].add(link_url)
                    outgoing_links[page_url] += 1
                    incoming_links[link_url] += 1
        
        # Find orphan pages (no incoming links)
        all_urls = set([page.get('url', '') for page in all_pages])
        orphan_pages = []
        for url in all_urls:
            if url != current_url and incoming_links.get(url, 0) == 0:
                orphan_pages.append(url)
        
        # Calculate link depth (clicks from homepage)
        homepage = None
        for page in all_pages:
            parsed = urlparse(page.get('url', ''))
            if parsed.path == '/' or parsed.path == '':
                homepage = page.get('url', '')
                break
        
        link_depths = {}
        if homepage:
            link_depths = self._calculate_link_depths(homepage, link_graph, all_urls)
        
        # Most linked pages
        most_linked = sorted(incoming_links.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Pages with most outbound links
        most_outbound = sorted(outgoing_links.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_pages': len(all_pages),
            'orphan_pages': orphan_pages,
            'orphan_count': len(orphan_pages),
            'most_linked_pages': [{'url': url, 'count': count} for url, count in most_linked],
            'most_outbound_pages': [{'url': url, 'count': count} for url, count in most_outbound],
            'average_incoming_links': sum(incoming_links.values()) / len(all_pages) if all_pages else 0,
            'average_outgoing_links': sum(outgoing_links.values()) / len(all_pages) if all_pages else 0,
            'link_depths': link_depths,
            'max_depth': max(link_depths.values()) if link_depths else 0
        }
    
    def _calculate_link_depths(self, start_url: str, link_graph: Dict, all_urls: Set[str]) -> Dict:
        """Calculate minimum clicks from homepage to each page"""
        depths = {start_url: 0}
        queue = [(start_url, 0)]
        visited = {start_url}
        
        while queue:
            current_url, depth = queue.pop(0)
            
            for linked_url in link_graph.get(current_url, []):
                if linked_url not in visited and linked_url in all_urls:
                    depths[linked_url] = depth + 1
                    visited.add(linked_url)
                    queue.append((linked_url, depth + 1))
        
        return depths

