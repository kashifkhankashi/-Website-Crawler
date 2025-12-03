"""
Competitor Analyzer - Compare two URLs side-by-side
"""
from typing import Dict, List, Optional, Tuple
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from collections import Counter


class CompetitorAnalyzer:
    """
    Analyze and compare two URLs:
    - Load speed comparison
    - Error comparison
    - On-page SEO differences
    - Keyword usage differences
    - Basic backlink comparison
    """
    
    def __init__(self):
        self.timeout = 30
    
    def analyze_competitors(self, url1: str, url2: str) -> Dict:
        """
        Analyze and compare two competitor URLs.
        
        Args:
            url1: First URL (your site)
            url2: Second URL (competitor)
            
        Returns:
            Dictionary with comparison results
        """
        print(f"Analyzing competitors: {url1} vs {url2}")
        
        # Analyze both URLs
        result1 = self._analyze_url(url1, "Your Site")
        result2 = self._analyze_url(url2, "Competitor")
        
        # Compare results
        comparison = self._compare_results(result1, result2)
        
        return {
            'url1': url1,
            'url2': url2,
            'your_site': result1,
            'competitor': result2,
            'comparison': comparison,
            'winner': self._determine_winner(comparison),
            'insights': self._generate_insights(comparison, result1, result2)
        }
    
    def _analyze_url(self, url: str, label: str) -> Dict:
        """Analyze a single URL."""
        start_time = time.time()
        
        try:
            # Fetch the page
            response = requests.get(url, timeout=self.timeout, allow_redirects=True)
            load_time = time.time() - start_time
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            title = self._extract_title(soup)
            meta_description = self._extract_meta_description(soup)
            h1_tags = self._extract_headings(soup, 'h1')
            h2_tags = self._extract_headings(soup, 'h2')
            h3_tags = self._extract_headings(soup, 'h3')
            images = self._extract_images(soup)
            links = self._extract_links(soup, url)
            text_content = self._extract_text_content(soup)
            word_count = len(text_content.split()) if text_content else 0
            
            # Extract keywords
            keywords = self._extract_keywords(text_content)
            
            # Check for errors
            has_errors = response.status_code >= 400
            error_count = 1 if has_errors else 0
            
            # Basic backlink check (check for external links pointing to this domain)
            external_links = links.get('external', [])
            backlink_indicators = self._check_backlink_indicators(soup, url)
            
            return {
                'url': url,
                'label': label,
                'status_code': response.status_code,
                'load_time': round(load_time, 2),
                'page_size': len(response.content),
                'has_errors': has_errors,
                'error_count': error_count,
                'title': title,
                'title_length': len(title) if title else 0,
                'meta_description': meta_description,
                'meta_description_length': len(meta_description) if meta_description else 0,
                'h1_count': len(h1_tags),
                'h1_tags': h1_tags,
                'h2_count': len(h2_tags),
                'h2_tags': h2_tags,
                'h3_count': len(h3_tags),
                'h3_tags': h3_tags,
                'word_count': word_count,
                'images_count': len(images),
                'images_with_alt': sum(1 for img in images if img.get('alt')),
                'internal_links_count': len(links.get('internal', [])),
                'external_links_count': len(external_links),
                'keywords': keywords,
                'top_keywords': keywords[:20],  # Top 20 keywords
                'backlink_indicators': backlink_indicators,
                'seo_score': self._calculate_basic_seo_score(title, meta_description, h1_tags, images, word_count)
            }
            
        except requests.exceptions.Timeout:
            return {
                'url': url,
                'label': label,
                'error': 'Timeout - Page took too long to load',
                'load_time': self.timeout,
                'has_errors': True,
                'error_count': 1
            }
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'label': label,
                'error': str(e),
                'has_errors': True,
                'error_count': 1
            }
        except Exception as e:
            return {
                'url': url,
                'label': label,
                'error': f'Analysis error: {str(e)}',
                'has_errors': True,
                'error_count': 1
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        if soup.title:
            return soup.title.get_text().strip()
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()
        return ''
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '').strip()
        return ''
    
    def _extract_headings(self, soup: BeautifulSoup, tag: str) -> List[str]:
        """Extract heading tags."""
        headings = []
        for h in soup.find_all(tag):
            text = h.get_text(strip=True)
            if text:
                headings.append(text)
        return headings
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract images with alt text."""
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            })
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Extract internal and external links."""
        parsed_base = urlparse(base_url)
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        internal_links = []
        external_links = []
        
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            if not href:
                continue
            
            # Resolve relative URLs
            if href.startswith('/'):
                full_url = f"{base_domain}{href}"
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = f"{base_url.rstrip('/')}/{href}"
            
            try:
                parsed = urlparse(full_url)
                if parsed.netloc == parsed_base.netloc:
                    internal_links.append(full_url)
                else:
                    external_links.append(full_url)
            except:
                pass
        
        return {
            'internal': list(set(internal_links)),
            'external': list(set(external_links))
        }
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content."""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_keywords(self, text: str) -> List[Tuple[str, int]]:
        """Extract top keywords from text."""
        if not text:
            return []
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Filter out common stop words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'their', 
                     'there', 'what', 'which', 'about', 'would', 'could', 'should', 'these', 
                     'those', 'them', 'they', 'were', 'where', 'when', 'than', 'then', 'more',
                     'most', 'some', 'such', 'only', 'just', 'also', 'very', 'much', 'many'}
        
        filtered_words = {word: count for word, count in word_counts.items() 
                         if word not in stop_words and count > 1}
        
        # Sort by frequency
        sorted_keywords = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords
    
    def _check_backlink_indicators(self, soup: BeautifulSoup, url: str) -> Dict:
        """Check for basic backlink indicators."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Check for social sharing buttons (indicates potential backlinks)
        social_indicators = {
            'has_facebook': bool(soup.find('a', href=re.compile(r'facebook\.com'))),
            'has_twitter': bool(soup.find('a', href=re.compile(r'twitter\.com'))),
            'has_linkedin': bool(soup.find('a', href=re.compile(r'linkedin\.com'))),
            'has_share_buttons': bool(soup.find(class_=re.compile(r'share|social', re.I)))
        }
        
        # Check for external mentions
        external_mentions = len(soup.find_all('a', href=re.compile(r'https?://(?!' + re.escape(domain) + r')')))
        
        return {
            'social_indicators': social_indicators,
            'external_mentions': external_mentions,
            'has_social_sharing': any(social_indicators.values())
        }
    
    def _calculate_basic_seo_score(self, title: str, meta_desc: str, h1_tags: List[str], 
                                   images: List[Dict], word_count: int) -> int:
        """Calculate a basic SEO score (0-100)."""
        score = 0
        
        # Title (20 points)
        if title:
            score += 10
            if 30 <= len(title) <= 60:
                score += 10
            elif len(title) > 0:
                score += 5
        
        # Meta description (15 points)
        if meta_desc:
            score += 10
            if 120 <= len(meta_desc) <= 160:
                score += 5
        
        # H1 (15 points)
        if len(h1_tags) == 1:
            score += 15
        elif len(h1_tags) > 0:
            score += 5
        
        # Images with alt (15 points)
        if images:
            images_with_alt = sum(1 for img in images if img.get('alt'))
            alt_ratio = images_with_alt / len(images) if images else 0
            score += int(15 * alt_ratio)
        
        # Word count (20 points)
        if word_count >= 500:
            score += 20
        elif word_count >= 300:
            score += 15
        elif word_count >= 100:
            score += 10
        elif word_count > 0:
            score += 5
        
        # Internal links (15 points)
        # This would need to be passed in, but for now we'll skip
        
        return min(100, score)
    
    def _compare_results(self, result1: Dict, result2: Dict) -> Dict:
        """Compare two analysis results."""
        comparison = {
            'load_speed': {
                'winner': 'your_site' if result1.get('load_time', 999) < result2.get('load_time', 999) else 'competitor',
                'difference': abs(result1.get('load_time', 0) - result2.get('load_time', 0)),
                'your_site': result1.get('load_time', 0),
                'competitor': result2.get('load_time', 0)
            },
            'errors': {
                'winner': 'your_site' if result1.get('error_count', 0) < result2.get('error_count', 0) else 'competitor',
                'your_site': result1.get('error_count', 0),
                'competitor': result2.get('error_count', 0)
            },
            'seo_score': {
                'winner': 'your_site' if result1.get('seo_score', 0) > result2.get('seo_score', 0) else 'competitor',
                'your_site': result1.get('seo_score', 0),
                'competitor': result2.get('seo_score', 0),
                'difference': result1.get('seo_score', 0) - result2.get('seo_score', 0)
            },
            'on_page_seo': {
                'title': {
                    'your_site': result1.get('title', ''),
                    'competitor': result2.get('title', ''),
                    'your_length': result1.get('title_length', 0),
                    'competitor_length': result2.get('title_length', 0)
                },
                'meta_description': {
                    'your_site': result1.get('meta_description', ''),
                    'competitor': result2.get('meta_description', ''),
                    'your_length': result1.get('meta_description_length', 0),
                    'competitor_length': result2.get('meta_description_length', 0)
                },
                'headings': {
                    'h1_count': {
                        'your_site': result1.get('h1_count', 0),
                        'competitor': result2.get('h1_count', 0)
                    },
                    'h2_count': {
                        'your_site': result1.get('h2_count', 0),
                        'competitor': result2.get('h2_count', 0)
                    }
                },
                'word_count': {
                    'your_site': result1.get('word_count', 0),
                    'competitor': result2.get('word_count', 0)
                },
                'images': {
                    'your_site': {
                        'total': result1.get('images_count', 0),
                        'with_alt': result1.get('images_with_alt', 0)
                    },
                    'competitor': {
                        'total': result2.get('images_count', 0),
                        'with_alt': result2.get('images_with_alt', 0)
                    }
                }
            },
            'keywords': {
                'common_keywords': self._find_common_keywords(
                    result1.get('keywords', []),
                    result2.get('keywords', [])
                ),
                'unique_to_your_site': self._find_unique_keywords(
                    result1.get('keywords', []),
                    result2.get('keywords', [])
                ),
                'unique_to_competitor': self._find_unique_keywords(
                    result2.get('keywords', []),
                    result1.get('keywords', [])
                )
            },
            'backlinks': {
                'your_site': result1.get('backlink_indicators', {}),
                'competitor': result2.get('backlink_indicators', {})
            }
        }
        
        return comparison
    
    def _find_common_keywords(self, keywords1: List[Tuple[str, int]], 
                              keywords2: List[Tuple[str, int]]) -> List[Dict]:
        """Find keywords common to both sites."""
        words1 = {word: count for word, count in keywords1}
        words2 = {word: count for word, count in keywords2}
        
        common = []
        for word in set(words1.keys()) & set(words2.keys()):
            common.append({
                'keyword': word,
                'your_count': words1[word],
                'competitor_count': words2[word],
                'total': words1[word] + words2[word]
            })
        
        # Sort by total frequency
        common.sort(key=lambda x: x['total'], reverse=True)
        return common[:20]  # Top 20 common keywords
    
    def _find_unique_keywords(self, keywords1: List[Tuple[str, int]], 
                             keywords2: List[Tuple[str, int]]) -> List[Dict]:
        """Find keywords unique to first list."""
        words1 = {word: count for word, count in keywords1}
        words2 = {word: count for word, count in keywords2}
        
        unique = []
        for word, count in words1.items():
            if word not in words2:
                unique.append({
                    'keyword': word,
                    'count': count
                })
        
        # Sort by frequency
        unique.sort(key=lambda x: x['count'], reverse=True)
        return unique[:20]  # Top 20 unique keywords
    
    def _determine_winner(self, comparison: Dict) -> Dict:
        """Determine overall winner."""
        wins = {
            'your_site': 0,
            'competitor': 0,
            'tie': 0
        }
        
        # Load speed
        if comparison['load_speed']['winner'] == 'your_site':
            wins['your_site'] += 1
        elif comparison['load_speed']['winner'] == 'competitor':
            wins['competitor'] += 1
        else:
            wins['tie'] += 1
        
        # Errors
        if comparison['errors']['winner'] == 'your_site':
            wins['your_site'] += 1
        elif comparison['errors']['winner'] == 'competitor':
            wins['competitor'] += 1
        else:
            wins['tie'] += 1
        
        # SEO Score
        if comparison['seo_score']['winner'] == 'your_site':
            wins['your_site'] += 1
        elif comparison['seo_score']['winner'] == 'competitor':
            wins['competitor'] += 1
        else:
            wins['tie'] += 1
        
        # Determine overall winner
        if wins['your_site'] > wins['competitor']:
            overall_winner = 'your_site'
        elif wins['competitor'] > wins['your_site']:
            overall_winner = 'competitor'
        else:
            overall_winner = 'tie'
        
        return {
            'overall': overall_winner,
            'wins': wins,
            'summary': f"Your site wins {wins['your_site']} categories, competitor wins {wins['competitor']} categories"
        }
    
    def _generate_insights(self, comparison: Dict, result1: Dict, result2: Dict) -> List[str]:
        """Generate actionable insights."""
        insights = []
        
        # Load speed insights
        if comparison['load_speed']['winner'] == 'competitor':
            diff = comparison['load_speed']['difference']
            insights.append(f"⚠️ Competitor loads {diff:.2f}s faster - optimize page speed")
        elif comparison['load_speed']['winner'] == 'your_site':
            diff = comparison['load_speed']['difference']
            insights.append(f"✅ Your site loads {diff:.2f}s faster - great job!")
        
        # SEO score insights
        seo_diff = comparison['seo_score']['difference']
        if seo_diff < -10:
            insights.append(f"⚠️ Competitor has {abs(seo_diff)} points higher SEO score - improve on-page SEO")
        elif seo_diff > 10:
            insights.append(f"✅ Your site has {seo_diff} points higher SEO score - excellent!")
        
        # Title insights
        your_title_len = comparison['on_page_seo']['title']['your_length']
        comp_title_len = comparison['on_page_seo']['title']['competitor_length']
        if your_title_len < 30:
            insights.append("⚠️ Your title is too short (aim for 30-60 characters)")
        if comp_title_len > your_title_len and comp_title_len <= 60:
            insights.append(f"💡 Competitor uses longer title ({comp_title_len} vs {your_title_len} chars)")
        
        # Word count insights
        your_words = comparison['on_page_seo']['word_count']['your_site']
        comp_words = comparison['on_page_seo']['word_count']['competitor']
        if comp_words > your_words * 1.5:
            insights.append(f"💡 Competitor has {comp_words - your_words} more words - consider expanding content")
        
        # Keyword insights
        common_count = len(comparison['keywords']['common_keywords'])
        unique_yours = len(comparison['keywords']['unique_to_your_site'])
        unique_comp = len(comparison['keywords']['unique_to_competitor'])
        
        if common_count > 0:
            insights.append(f"📊 {common_count} common keywords found - you're targeting similar topics")
        if unique_comp > unique_yours:
            insights.append(f"💡 Competitor uses {unique_comp - unique_yours} more unique keywords - research their keyword strategy")
        
        return insights

