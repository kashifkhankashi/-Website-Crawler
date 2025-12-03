"""
Advanced Competitor Analyzer - Deep, comprehensive competitor analysis
"""
from typing import Dict, List, Optional, Tuple
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from collections import Counter
import json

# Import new analysis modules
try:
    from pagespeed_analyzer import PageSpeedAnalyzer
    PAGESPEED_AVAILABLE = True
except ImportError:
    PAGESPEED_AVAILABLE = False
    PageSpeedAnalyzer = None

try:
    from link_analyzer import LinkAnalyzer
    LINK_ANALYZER_AVAILABLE = True
except ImportError:
    LINK_ANALYZER_AVAILABLE = False
    LinkAnalyzer = None

try:
    from content_analyzer import ContentAnalyzer
    CONTENT_ANALYZER_AVAILABLE = True
except ImportError:
    CONTENT_ANALYZER_AVAILABLE = False
    ContentAnalyzer = None

try:
    from visual_analyzer import VisualAnalyzer
    VISUAL_ANALYZER_AVAILABLE = True
except ImportError:
    VISUAL_ANALYZER_AVAILABLE = False
    VisualAnalyzer = None

try:
    from accessibility_analyzer import AccessibilityAnalyzer
    ACCESSIBILITY_AVAILABLE = True
except ImportError:
    ACCESSIBILITY_AVAILABLE = False
    AccessibilityAnalyzer = None


class AdvancedCompetitorAnalyzer:
    """
    Advanced competitor analysis with deep insights:
    - Comprehensive performance metrics
    - Deep SEO analysis
    - Advanced keyword research
    - Content structure analysis
    - Technical SEO comparison
    - Backlink indicators
    - Mobile-friendliness
    - Security analysis
    """
    
    def __init__(self, pagespeed_api_key: Optional[str] = None):
        self.timeout = 45
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Initialize analyzers
        if PAGESPEED_AVAILABLE and PageSpeedAnalyzer:
            self.pagespeed = PageSpeedAnalyzer(pagespeed_api_key)
        else:
            self.pagespeed = None
        
        if LINK_ANALYZER_AVAILABLE and LinkAnalyzer:
            self.link_analyzer = LinkAnalyzer()
        else:
            self.link_analyzer = None
        
        if CONTENT_ANALYZER_AVAILABLE and ContentAnalyzer:
            self.content_analyzer = ContentAnalyzer()
        else:
            self.content_analyzer = None
        
        if VISUAL_ANALYZER_AVAILABLE and VisualAnalyzer:
            self.visual_analyzer = VisualAnalyzer()
        else:
            self.visual_analyzer = None
        
        if ACCESSIBILITY_AVAILABLE and AccessibilityAnalyzer:
            self.accessibility_analyzer = AccessibilityAnalyzer()
        else:
            self.accessibility_analyzer = None
    
    def analyze_competitors(self, url1: str, url2: str) -> Dict:
        """
        Perform deep competitor analysis.
        
        Args:
            url1: Your website URL
            url2: Competitor URL
            
        Returns:
            Comprehensive comparison results
        """
        print(f"Starting advanced competitor analysis: {url1} vs {url2}")
        
        # Analyze both URLs with comprehensive checks
        result1 = self._analyze_url_comprehensive(url1, "Your Site")
        result2 = self._analyze_url_comprehensive(url2, "Competitor")
        
        # Deep comparison
        comparison = self._deep_compare_results(result1, result2)
        
        # Content Gap Analysis
        content_gaps = None
        if self.content_analyzer and result1.get('content_intelligence') and result2.get('content_intelligence'):
            try:
                content_gaps = self.content_analyzer.detect_content_gaps(
                    result1['content_intelligence'],
                    result2['content_intelligence']
                )
            except Exception as e:
                print(f"Content gap analysis error: {e}")
        
        # Visual Comparison
        visual_comparison = None
        if (self.visual_analyzer and 
            result1.get('desktop_screenshot') and result2.get('desktop_screenshot') and
            not result1['desktop_screenshot'].get('has_error') and
            not result2['desktop_screenshot'].get('has_error')):
            try:
                visual_comparison = self.visual_analyzer.compare_screenshots(
                    result1['desktop_screenshot'],
                    result2['desktop_screenshot']
                )
            except Exception as e:
                print(f"Visual comparison error: {e}")
        
        # Generate advanced insights
        insights = self._generate_advanced_insights(comparison, result1, result2)
        
        # Calculate competitive advantage score
        advantage_score = self._calculate_advantage_score(comparison, result1, result2)
        
        return {
            'url1': url1,
            'url2': url2,
            'your_site': result1,
            'competitor': result2,
            'comparison': comparison,
            'advantage_score': advantage_score,
            'winner': self._determine_winner_advanced(comparison, advantage_score),
            'insights': insights,
            'recommendations': self._generate_recommendations(comparison, result1, result2),
            'content_gaps': content_gaps,
            'visual_comparison': visual_comparison,
            'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _analyze_url_comprehensive(self, url: str, label: str) -> Dict:
        """Comprehensive URL analysis with deep checks."""
        start_time = time.time()
        
        try:
            # Normalize URL
            if not url.startswith('http'):
                url = 'https://' + url
            
            # Fetch with headers
            response = requests.get(url, timeout=self.timeout, headers=self.headers, allow_redirects=True, verify=False)
            load_time = time.time() - start_time
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract comprehensive data
            analysis = {
                'url': response.url,  # Final URL after redirects
                'label': label,
                'status_code': response.status_code,
                'load_time': round(load_time, 3),
                'page_size': len(response.content),
                'html_size': len(response.text),
                'redirect_count': len(response.history),
                'final_url': response.url,
            }
            
            # Basic SEO
            analysis.update(self._extract_seo_data(soup, url))
            
            # Content analysis
            analysis.update(self._analyze_content(soup))
            
            # Technical SEO
            analysis.update(self._analyze_technical_seo(soup, url, response))
            
            # Performance indicators
            analysis.update(self._analyze_performance_indicators(soup, response))
            
            # Mobile-friendliness
            analysis.update(self._analyze_mobile_friendliness(soup))
            
            # Security
            analysis.update(self._analyze_security(response))
            
            # Backlink indicators
            backlink_data = self._analyze_backlink_indicators(soup, url)
            analysis['backlink_indicators'] = backlink_data
            
            # Content structure
            analysis.update(self._analyze_content_structure(soup))
            
            # Calculate overall scores
            analysis['seo_score'] = self._calculate_comprehensive_seo_score(analysis)
            analysis['performance_score'] = self._calculate_performance_score(analysis)
            analysis['technical_score'] = self._calculate_technical_score(analysis)
            analysis['overall_score'] = (
                analysis['seo_score'] * 0.4 +
                analysis['performance_score'] * 0.3 +
                analysis['technical_score'] * 0.3
            )
            
            # Advanced Link Analysis (always run, with fallback)
            try:
                if self.link_analyzer:
                    link_analysis = self.link_analyzer.analyze_links(soup, url)
                    analysis['link_analysis'] = link_analysis
                else:
                    # Basic link analysis fallback - always provide data
                    links = soup.find_all('a', href=True)
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc
                    
                    internal_links = []
                    external_links = []
                    anchor_texts = []
                    
                    for link in links:
                        href = link.get('href', '').strip()
                        if not href or href.startswith('#'):
                            continue
                        
                        anchor_text = link.get_text(strip=True)
                        if anchor_text:
                            anchor_texts.append(anchor_text)
                        
                        if href.startswith('http'):
                            try:
                                link_parsed = urlparse(href)
                                if link_parsed.netloc == domain:
                                    internal_links.append(href)
                                else:
                                    external_links.append(href)
                            except:
                                pass
                        elif href.startswith('/'):
                            internal_links.append(href)
                    
                    # Basic anchor analysis
                    keyword_rich = 0
                    generic = 0
                    generic_anchors = {'click here', 'read more', 'here', 'link', 'more'}
                    
                    for anchor in anchor_texts:
                        anchor_lower = anchor.lower().strip()
                        if anchor_lower in generic_anchors:
                            generic += 1
                        elif len(anchor_lower.split()) >= 2:
                            keyword_rich += 1
                    
                    analysis['link_analysis'] = {
                        'link_metrics': {
                            'internal_links_count': len(internal_links),
                            'external_links_count': len(external_links)
                        },
                        'anchor_analysis': {
                            'keyword_rich': keyword_rich,
                            'generic': generic,
                            'keyword_rich_ratio': keyword_rich / len(anchor_texts) if anchor_texts else 0,
                            'total': len(anchor_texts)
                        }
                    }
            except Exception as e:
                print(f"Link analysis error: {e}")
                # Still provide basic data
                analysis['link_analysis'] = {
                    'link_metrics': {'internal_links_count': 0, 'external_links_count': 0},
                    'anchor_analysis': {'keyword_rich': 0, 'generic': 0, 'keyword_rich_ratio': 0}
                }
            
            # Content Intelligence (always run, with fallback)
            try:
                if self.content_analyzer:
                    content_analysis = self.content_analyzer.analyze_content(soup, url)
                    analysis['content_intelligence'] = content_analysis
                else:
                    # Basic content analysis fallback
                    text = soup.get_text()
                    words = text.split()
                    analysis['content_intelligence'] = {
                        'word_count': len(words),
                        'character_count': len(text),
                        'topics': {'main_topics': [], 'topic_count': 0}
                    }
            except Exception as e:
                print(f"Content analysis error: {e}")
                # Provide basic fallback
                text = soup.get_text() if soup else ''
                analysis['content_intelligence'] = {
                    'word_count': len(text.split()),
                    'character_count': len(text),
                    'topics': {'main_topics': [], 'topic_count': 0}
                }
            
            # Accessibility Analysis (always run, with fallback)
            try:
                if self.accessibility_analyzer:
                    accessibility = self.accessibility_analyzer.analyze_accessibility(soup, url)
                    analysis['accessibility'] = accessibility
                else:
                    # Basic accessibility fallback - always provide data
                    images = soup.find_all('img')
                    with_alt = len([img for img in images if img.get('alt')])
                    alt_coverage = round((with_alt / len(images) * 100) if images else 0, 1)
                    
                    # Check semantic HTML
                    semantic_elements = {
                        'header': len(soup.find_all('header')),
                        'footer': len(soup.find_all('footer')),
                        'main': len(soup.find_all('main')),
                        'nav': len(soup.find_all('nav'))
                    }
                    semantic_score = sum(1 for count in semantic_elements.values() if count > 0) * 20
                    
                    # Basic WCAG score
                    wcag_score = alt_coverage * 0.5 + min(50, semantic_score)
                    
                    analysis['accessibility'] = {
                        'wcag_score': round(wcag_score, 1),
                        'wcag_level': 'A (Basic)' if wcag_score >= 60 else 'Non-compliant',
                        'image_analysis': {
                            'alt_coverage': alt_coverage,
                            'total': len(images),
                            'with_alt': with_alt
                        },
                        'form_analysis': {
                            'label_coverage': 0,
                            'total_inputs': len(soup.find_all(['input', 'textarea', 'select']))
                        },
                        'semantic_analysis': {
                            'score': min(100, semantic_score),
                            'elements': semantic_elements
                        }
                    }
            except Exception as e:
                print(f"Accessibility analysis error: {e}")
                # Provide basic fallback
                images = soup.find_all('img') if soup else []
                with_alt = len([img for img in images if img.get('alt')]) if images else 0
                alt_coverage = round((with_alt / len(images) * 100) if images else 0, 1)
                analysis['accessibility'] = {
                    'wcag_score': alt_coverage,
                    'wcag_level': 'A (Basic)',
                    'image_analysis': {'alt_coverage': alt_coverage},
                    'form_analysis': {'label_coverage': 0},
                    'semantic_analysis': {'score': 0}
                }
            
            # Visual Analysis (screenshots) - optional, can be slow
            try:
                if self.visual_analyzer and self.visual_analyzer.playwright_available:
                    # Desktop screenshot
                    desktop_screenshot = self.visual_analyzer.capture_desktop_screenshot(url)
                    if desktop_screenshot and not desktop_screenshot.get('has_error'):
                        analysis['desktop_screenshot'] = desktop_screenshot
                        # Analyze visual hierarchy
                        if desktop_screenshot.get('screenshot'):
                            visual_analysis = self.visual_analyzer.analyze_visual_hierarchy(
                                desktop_screenshot['screenshot']
                            )
                            analysis['visual_analysis'] = visual_analysis
            except Exception as e:
                print(f"Visual analysis error (optional): {e}")
                # Don't set if failed - it's optional
            
            # Google PageSpeed Insights (optional, requires API key)
            try:
                if self.pagespeed:
                    print(f"Running PageSpeed analysis for {url}...")
                    pagespeed_mobile = self.pagespeed.analyze_url(url, 'mobile')
                    if not pagespeed_mobile.get('has_error'):
                        analysis['pagespeed_mobile'] = pagespeed_mobile
                    
                    time.sleep(1)  # Rate limiting
                    
                    pagespeed_desktop = self.pagespeed.analyze_url(url, 'desktop')
                    if not pagespeed_desktop.get('has_error'):
                        analysis['pagespeed_desktop'] = pagespeed_desktop
            except Exception as e:
                print(f"PageSpeed analysis error (optional): {e}")
                # Don't set if failed - it's optional
            
            return analysis
            
        except requests.exceptions.Timeout:
            return self._create_error_result(url, label, 'Timeout - Page took too long to load')
        except requests.exceptions.SSLError:
            return self._create_error_result(url, label, 'SSL Certificate Error')
        except requests.exceptions.ConnectionError:
            return self._create_error_result(url, label, 'Connection Error - Site may be down')
        except Exception as e:
            return self._create_error_result(url, label, f'Analysis error: {str(e)}')
    
    def _create_error_result(self, url: str, label: str, error: str) -> Dict:
        """Create error result structure."""
        return {
            'url': url,
            'label': label,
            'error': error,
            'has_errors': True,
            'error_count': 1,
            'load_time': self.timeout,
            'seo_score': 0,
            'performance_score': 0,
            'technical_score': 0,
            'overall_score': 0
        }
    
    def _extract_seo_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract comprehensive SEO data."""
        # Title
        title = ''
        if soup.title:
            title = soup.title.get_text().strip()
        og_title = soup.find('meta', property='og:title')
        if not title and og_title:
            title = og_title.get('content', '').strip()
        
        # Meta description
        meta_desc = ''
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_desc_tag:
            meta_desc = meta_desc_tag.get('content', '').strip()
        og_desc = soup.find('meta', property='og:description')
        if not meta_desc and og_desc:
            meta_desc = og_desc.get('content', '').strip()
        
        # Meta keywords
        meta_keywords = ''
        meta_kw_tag = soup.find('meta', attrs={'name': 'keywords'})
        if meta_kw_tag:
            meta_keywords = meta_kw_tag.get('content', '').strip()
        
        # Canonical
        canonical = ''
        canonical_tag = soup.find('link', rel=lambda v: v and 'canonical' in v.lower())
        if canonical_tag:
            canonical = canonical_tag.get('href', '').strip()
            if canonical and not canonical.startswith('http'):
                canonical = urljoin(url, canonical)
        
        # Headings
        def get_headings(tag):
            return [h.get_text(strip=True) for h in soup.find_all(tag) if h.get_text(strip=True)]
        
        h1_tags = get_headings('h1')
        h2_tags = get_headings('h2')
        h3_tags = get_headings('h3')
        h4_tags = get_headings('h4')
        h5_tags = get_headings('h5')
        h6_tags = get_headings('h6')
        
        # Open Graph tags
        og_tags = {}
        for og in soup.find_all('meta', property=re.compile(r'^og:')):
            prop = og.get('property', '')
            content = og.get('content', '')
            if prop and content:
                og_tags[prop] = content
        
        # Twitter Card tags
        twitter_tags = {}
        for tw in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = tw.get('name', '')
            content = tw.get('content', '')
            if name and content:
                twitter_tags[name] = content
        
        # Schema markup
        schema_types = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                schema_data = json.loads(script.string)
                if isinstance(schema_data, dict) and '@type' in schema_data:
                    schema_types.append(schema_data.get('@type', ''))
                elif isinstance(schema_data, list):
                    for item in schema_data:
                        if isinstance(item, dict) and '@type' in item:
                            schema_types.append(item.get('@type', ''))
            except:
                pass
        
        return {
            'title': title,
            'title_length': len(title),
            'meta_description': meta_desc,
            'meta_description_length': len(meta_desc),
            'meta_keywords': meta_keywords,
            'canonical_url': canonical,
            'h1_tags': h1_tags,
            'h1_count': len(h1_tags),
            'h2_tags': h2_tags,
            'h2_count': len(h2_tags),
            'h3_tags': h3_tags,
            'h3_count': len(h3_tags),
            'h4_count': len(h4_tags),
            'h5_count': len(h5_tags),
            'h6_count': len(h6_tags),
            'og_tags': og_tags,
            'og_tags_count': len(og_tags),
            'twitter_tags': twitter_tags,
            'twitter_tags_count': len(twitter_tags),
            'schema_types': schema_types,
            'schema_count': len(schema_types)
        }
    
    def _analyze_content(self, soup: BeautifulSoup) -> Dict:
        """Deep content analysis."""
        # Remove scripts and styles
        for script in soup(["script", "style", "noscript", "meta", "link"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Word count
        words = text_content.split()
        word_count = len(words)
        
        # Character count
        char_count = len(text_content)
        char_count_no_spaces = len(text_content.replace(' ', ''))
        
        # Paragraph count
        paragraphs = soup.find_all('p')
        paragraph_count = len([p for p in paragraphs if p.get_text(strip=True)])
        
        # Extract keywords with advanced analysis
        keywords = self._extract_keywords_advanced(text_content)
        
        # Content density
        content_density = self._calculate_content_density(soup)
        
        # Readability
        readability = self._calculate_readability_advanced(text_content, word_count)
        
        return {
            'text_content': text_content[:5000],  # First 5000 chars for analysis
            'word_count': word_count,
            'character_count': char_count,
            'character_count_no_spaces': char_count_no_spaces,
            'paragraph_count': paragraph_count,
            'keywords': keywords,
            'top_keywords': keywords[:30],
            'keyword_diversity': len(set([k[0] for k in keywords])),
            'content_density': content_density,
            'readability_score': readability['score'],
            'readability_grade': readability['grade'],
            'avg_sentence_length': readability['avg_sentence_length'],
            'avg_word_length': readability['avg_word_length']
        }
    
    def _extract_keywords_advanced(self, text: str) -> List[Tuple[str, int, float]]:
        """Advanced keyword extraction with TF-IDF approximation."""
        if not text:
            return []
        
        # Convert to lowercase
        text_lower = text.lower()
        
        # Extract words (4+ characters)
        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        
        if not words:
            return []
        
        # Stop words list (extended)
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'their',
            'there', 'what', 'which', 'about', 'would', 'could', 'should', 'these',
            'those', 'them', 'they', 'were', 'where', 'when', 'than', 'then', 'more',
            'most', 'some', 'such', 'only', 'just', 'also', 'very', 'much', 'many',
            'into', 'over', 'after', 'under', 'through', 'during', 'before', 'above',
            'below', 'between', 'among', 'within', 'without', 'against', 'toward',
            'towards', 'around', 'throughout', 'beside', 'besides', 'except', 'beyond'
        }
        
        # Count word frequencies
        word_counts = Counter(words)
        total_words = len(words)
        
        # Calculate importance score (TF * IDF approximation)
        keywords = []
        for word, count in word_counts.items():
            if word not in stop_words and count > 1:
                # TF (Term Frequency)
                tf = count / total_words
                
                # Simple IDF approximation (inverse document frequency)
                # More unique words get higher score
                idf = 1.0 / (1.0 + count / total_words)
                
                # Combined score
                importance = tf * idf * count
                
                keywords.append((word, count, importance))
        
        # Sort by importance
        keywords.sort(key=lambda x: x[2], reverse=True)
        
        return keywords
    
    def _calculate_content_density(self, soup: BeautifulSoup) -> Dict:
        """Calculate content density metrics."""
        # Count different elements
        divs = len(soup.find_all('div'))
        spans = len(soup.find_all('span'))
        paragraphs = len(soup.find_all('p'))
        lists = len(soup.find_all(['ul', 'ol']))
        images = len(soup.find_all('img'))
        links = len(soup.find_all('a'))
        
        total_elements = divs + spans + paragraphs + lists
        
        return {
            'div_count': divs,
            'span_count': spans,
            'paragraph_count': paragraphs,
            'list_count': lists,
            'image_count': images,
            'link_count': links,
            'total_elements': total_elements,
            'content_ratio': paragraphs / total_elements if total_elements > 0 else 0
        }
    
    def _calculate_readability_advanced(self, text: str, word_count: int) -> Dict:
        """Calculate advanced readability metrics."""
        if not text or word_count == 0:
            return {
                'score': 0,
                'grade': 'N/A',
                'avg_sentence_length': 0,
                'avg_word_length': 0
            }
        
        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences) if sentences else 1
        
        # Count syllables (approximate)
        vowels = 'aeiouy'
        syllables = sum(1 for char in text.lower() if char in vowels)
        if syllables == 0:
            syllables = word_count
        
        # Calculate averages
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        avg_syllables_per_word = syllables / word_count if word_count > 0 else 0
        avg_word_length = sum(len(word) for word in text.split()) / word_count if word_count > 0 else 0
        
        # Flesch Reading Ease
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))
        
        # Grade level
        if flesch_score >= 90:
            grade = 'Very Easy (5th grade)'
        elif flesch_score >= 80:
            grade = 'Easy (6th grade)'
        elif flesch_score >= 70:
            grade = 'Fairly Easy (7th grade)'
        elif flesch_score >= 60:
            grade = 'Standard (8th-9th grade)'
        elif flesch_score >= 50:
            grade = 'Fairly Difficult (10th-12th grade)'
        elif flesch_score >= 30:
            grade = 'Difficult (College)'
        else:
            grade = 'Very Difficult (College Graduate)'
        
        return {
            'score': round(flesch_score, 1),
            'grade': grade,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_word_length': round(avg_word_length, 1),
            'syllables_per_word': round(avg_syllables_per_word, 2)
        }
    
    def _analyze_technical_seo(self, soup: BeautifulSoup, url: str, response) -> Dict:
        """Analyze technical SEO factors."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Robots meta
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        robots_content = robots_meta.get('content', '').lower() if robots_meta else ''
        
        # Viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        has_viewport = bool(viewport)
        
        # Language
        lang = soup.html.get('lang', '') if soup.html else ''
        
        # Images analysis
        images = soup.find_all('img')
        images_data = []
        images_with_alt = 0
        images_without_alt = 0
        large_images = 0
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            width = img.get('width', '')
            height = img.get('height', '')
            
            images_data.append({
                'src': src,
                'alt': alt,
                'width': width,
                'height': height
            })
            
            if alt and alt.strip():
                images_with_alt += 1
            else:
                images_without_alt += 1
            
            # Check for large images (indicator)
            if width and isinstance(width, str) and width.replace('px', '').isdigit():
                if int(width.replace('px', '')) > 1000:
                    large_images += 1
        
        # Links analysis
        links = soup.find_all('a', href=True)
        internal_links = []
        external_links = []
        nofollow_links = 0
        
        for link in links:
            href = link.get('href', '')
            rel = link.get('rel', [])
            is_nofollow = 'nofollow' in [r.lower() for r in rel] if isinstance(rel, list) else 'nofollow' in str(rel).lower()
            
            if is_nofollow:
                nofollow_links += 1
            
            if href.startswith('http'):
                parsed_link = urlparse(href)
                if parsed_link.netloc == domain:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            elif href.startswith('/'):
                internal_links.append(urljoin(url, href))
        
        # Check for sitemap reference
        sitemap_link = soup.find('link', rel='sitemap')
        has_sitemap_link = bool(sitemap_link)
        
        # Check for RSS feed
        rss_link = soup.find('link', type='application/rss+xml')
        has_rss = bool(rss_link)
        
        return {
            'robots_meta': robots_content,
            'has_viewport': has_viewport,
            'language': lang,
            'images': images_data,
            'images_count': len(images),
            'images_with_alt': images_with_alt,
            'images_without_alt': images_without_alt,
            'images_alt_coverage': round((images_with_alt / len(images) * 100) if images else 0, 1),
            'large_images_count': large_images,
            'internal_links': list(set(internal_links)),
            'internal_links_count': len(set(internal_links)),
            'external_links': list(set(external_links)),
            'external_links_count': len(set(external_links)),
            'nofollow_links_count': nofollow_links,
            'has_sitemap_link': has_sitemap_link,
            'has_rss_feed': has_rss
        }
    
    def _analyze_performance_indicators(self, soup: BeautifulSoup, response) -> Dict:
        """Analyze performance indicators."""
        # Scripts
        scripts = soup.find_all('script')
        inline_scripts = len([s for s in scripts if not s.get('src')])
        external_scripts = len([s for s in scripts if s.get('src')])
        
        # Stylesheets
        stylesheets = soup.find_all('link', rel='stylesheet')
        stylesheet_count = len(stylesheets)
        
        # Check for async/defer
        scripts_with_async = len([s for s in scripts if s.get('async')])
        scripts_with_defer = len([s for s in scripts if s.get('defer')])
        
        # Check for render-blocking
        render_blocking = stylesheet_count + (external_scripts - scripts_with_async - scripts_with_defer)
        
        # Check for large inline styles
        inline_styles = soup.find_all('style')
        large_inline_styles = len([s for s in inline_styles if len(s.string or '') > 5000])
        
        # Font loading
        font_links = soup.find_all('link', rel=lambda v: v and 'font' in v.lower())
        font_count = len(font_links)
        
        # Preconnect/prefetch
        preconnect = len(soup.find_all('link', rel='preconnect'))
        prefetch = len(soup.find_all('link', rel='prefetch'))
        dns_prefetch = len(soup.find_all('link', rel='dns-prefetch'))
        
        return {
            'scripts_count': len(scripts),
            'inline_scripts': inline_scripts,
            'external_scripts': external_scripts,
            'scripts_with_async': scripts_with_async,
            'scripts_with_defer': scripts_with_defer,
            'stylesheets_count': stylesheet_count,
            'render_blocking_resources': render_blocking,
            'large_inline_styles': large_inline_styles,
            'font_count': font_count,
            'preconnect_count': preconnect,
            'prefetch_count': prefetch,
            'dns_prefetch_count': dns_prefetch,
            'performance_optimizations': preconnect + prefetch + dns_prefetch
        }
    
    def _analyze_mobile_friendliness(self, soup: BeautifulSoup) -> Dict:
        """Analyze mobile-friendliness."""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        has_viewport = bool(viewport)
        
        viewport_content = viewport.get('content', '') if viewport else ''
        
        # Check for mobile-specific meta tags
        has_mobile_optimized = 'width=device-width' in viewport_content.lower()
        
        # Check for touch icons
        apple_touch_icon = soup.find('link', rel='apple-touch-icon')
        has_touch_icon = bool(apple_touch_icon)
        
        # Check for responsive images (srcset)
        images_with_srcset = len(soup.find_all('img', srcset=True))
        
        # Check for mobile menu indicators
        mobile_menu_indicators = [
            'mobile-menu', 'mobile-nav', 'hamburger', 'menu-toggle', 'nav-toggle'
        ]
        has_mobile_menu = any(
            soup.find(attrs={'class': re.compile(indicator, re.I)}) or
            soup.find(attrs={'id': re.compile(indicator, re.I)})
            for indicator in mobile_menu_indicators
        )
        
        return {
            'has_viewport': has_viewport,
            'has_mobile_optimized': has_mobile_optimized,
            'has_touch_icon': has_touch_icon,
            'images_with_srcset': images_with_srcset,
            'has_mobile_menu': has_mobile_menu,
            'mobile_score': self._calculate_mobile_score(has_viewport, has_mobile_optimized, images_with_srcset)
        }
    
    def _calculate_mobile_score(self, has_viewport: bool, is_optimized: bool, responsive_images: int) -> int:
        """Calculate mobile-friendliness score."""
        score = 0
        if has_viewport:
            score += 30
        if is_optimized:
            score += 30
        if responsive_images > 0:
            score += min(40, responsive_images * 5)
        return score
    
    def _analyze_security(self, response) -> Dict:
        """Analyze security headers and indicators."""
        headers = response.headers
        
        security_headers = {
            'https': response.url.startswith('https://'),
            'x_frame_options': headers.get('X-Frame-Options', ''),
            'x_content_type_options': headers.get('X-Content-Type-Options', ''),
            'x_xss_protection': headers.get('X-XSS-Protection', ''),
            'strict_transport_security': headers.get('Strict-Transport-Security', ''),
            'content_security_policy': headers.get('Content-Security-Policy', ''),
            'referrer_policy': headers.get('Referrer-Policy', '')
        }
        
        # Count security headers
        security_count = sum(1 for v in security_headers.values() if v)
        
        return {
            'security_headers': security_headers,
            'security_headers_count': security_count,
            'security_score': min(100, security_count * 15)
        }
    
    def _analyze_backlink_indicators(self, soup: BeautifulSoup, url: str) -> Dict:
        """Advanced backlink indicator analysis."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Social sharing buttons
        social_platforms = {
            'facebook': bool(soup.find('a', href=re.compile(r'facebook\.com|fb\.com'))),
            'twitter': bool(soup.find('a', href=re.compile(r'twitter\.com|x\.com'))),
            'linkedin': bool(soup.find('a', href=re.compile(r'linkedin\.com'))),
            'instagram': bool(soup.find('a', href=re.compile(r'instagram\.com'))),
            'youtube': bool(soup.find('a', href=re.compile(r'youtube\.com'))),
            'pinterest': bool(soup.find('a', href=re.compile(r'pinterest\.com'))),
        }
        
        # External links count (potential backlink sources)
        all_links = soup.find_all('a', href=True)
        external_domains = set()
        for link in all_links:
            href = link.get('href', '')
            if href.startswith('http'):
                try:
                    link_domain = urlparse(href).netloc
                    if link_domain != domain:
                        external_domains.add(link_domain)
                except:
                    pass
        
        # Check for citation indicators
        citation_indicators = [
            'as seen on', 'featured in', 'mentioned in', 'cited by',
            'press', 'media', 'news', 'awards', 'testimonials'
        ]
        has_citations = any(
            soup.find(string=re.compile(indicator, re.I))
            for indicator in citation_indicators
        )
        
        # Check for author/authority indicators
        has_author_tag = bool(soup.find('meta', attrs={'name': 'author'}))
        has_author_link = bool(soup.find('a', rel='author'))
        
        return {
            'social_platforms': social_platforms,
            'social_count': sum(social_platforms.values()),
            'external_domains_count': len(external_domains),
            'external_domains': list(external_domains)[:20],  # Top 20
            'has_citations': has_citations,
            'has_author_tag': has_author_tag,
            'has_author_link': has_author_link,
            'backlink_potential_score': self._calculate_backlink_potential(
                social_platforms, len(external_domains), has_citations
            )
        }
    
    def _calculate_backlink_potential(self, social: Dict, external_domains: int, has_citations: bool) -> int:
        """Calculate backlink potential score."""
        score = 0
        score += sum(social.values()) * 10  # Social sharing
        score += min(30, external_domains * 2)  # External domains
        if has_citations:
            score += 20
        return min(100, score)
    
    def _analyze_content_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze content structure and organization."""
        # Navigation
        nav_elements = soup.find_all('nav')
        nav_count = len(nav_elements)
        
        # Lists
        ul_lists = len(soup.find_all('ul'))
        ol_lists = len(soup.find_all('ol'))
        
        # Tables
        tables = len(soup.find_all('table'))
        
        # Forms
        forms = len(soup.find_all('form'))
        
        # Semantic HTML5 elements
        semantic_elements = {
            'header': len(soup.find_all('header')),
            'footer': len(soup.find_all('footer')),
            'main': len(soup.find_all('main')),
            'article': len(soup.find_all('article')),
            'section': len(soup.find_all('section')),
            'aside': len(soup.find_all('aside')),
            'nav': nav_count
        }
        
        semantic_score = sum(1 for count in semantic_elements.values() if count > 0) * 15
        
        return {
            'nav_count': nav_count,
            'list_count': ul_lists + ol_lists,
            'table_count': tables,
            'form_count': forms,
            'semantic_elements': semantic_elements,
            'semantic_score': min(100, semantic_score),
            'structure_score': self._calculate_structure_score(semantic_elements, nav_count)
        }
    
    def _calculate_structure_score(self, semantic: Dict, nav_count: int) -> int:
        """Calculate content structure score."""
        score = 0
        if semantic['header'] > 0:
            score += 20
        if semantic['footer'] > 0:
            score += 20
        if semantic['main'] > 0 or semantic['article'] > 0:
            score += 20
        if nav_count > 0:
            score += 20
        if semantic['section'] > 0:
            score += 20
        return min(100, score)
    
    def _calculate_comprehensive_seo_score(self, analysis: Dict) -> int:
        """Calculate comprehensive SEO score (0-100)."""
        score = 0
        
        # Title (15 points)
        if analysis.get('title'):
            score += 10
            title_len = analysis.get('title_length', 0)
            if 30 <= title_len <= 60:
                score += 5
            elif title_len > 0:
                score += 2
        
        # Meta description (10 points)
        if analysis.get('meta_description'):
            score += 7
            desc_len = analysis.get('meta_description_length', 0)
            if 120 <= desc_len <= 160:
                score += 3
        
        # Headings (15 points)
        h1_count = analysis.get('h1_count', 0)
        h2_count = analysis.get('h2_count', 0)
        if h1_count == 1:
            score += 10
        if h2_count >= 2:
            score += 5
        
        # Images with alt (10 points)
        alt_coverage = analysis.get('images_alt_coverage', 0)
        score += int(10 * alt_coverage / 100)
        
        # Word count (15 points)
        word_count = analysis.get('word_count', 0)
        if word_count >= 1000:
            score += 15
        elif word_count >= 500:
            score += 10
        elif word_count >= 300:
            score += 5
        
        # Technical SEO (15 points)
        if analysis.get('canonical_url'):
            score += 5
        if analysis.get('og_tags_count', 0) >= 3:
            score += 5
        if analysis.get('schema_count', 0) > 0:
            score += 5
        
        # Mobile (10 points)
        score += int(analysis.get('mobile_score', 0) / 10)
        
        # Structure (10 points)
        score += int(analysis.get('structure_score', 0) / 10)
        
        return min(100, score)
    
    def _calculate_performance_score(self, analysis: Dict) -> int:
        """Calculate performance score (0-100)."""
        score = 100
        
        # Load time penalty
        load_time = analysis.get('load_time', 999)
        if load_time > 5:
            score -= 30
        elif load_time > 3:
            score -= 20
        elif load_time > 2:
            score -= 10
        
        # Page size penalty
        page_size = analysis.get('page_size', 0)
        if page_size > 5 * 1024 * 1024:  # 5MB
            score -= 20
        elif page_size > 2 * 1024 * 1024:  # 2MB
            score -= 10
        
        # Render-blocking penalty
        render_blocking = analysis.get('render_blocking_resources', 0)
        score -= min(20, render_blocking * 2)
        
        # Large images penalty
        large_images = analysis.get('large_images_count', 0)
        score -= min(10, large_images)
        
        return max(0, score)
    
    def _calculate_technical_score(self, analysis: Dict) -> int:
        """Calculate technical SEO score (0-100)."""
        score = 0
        
        # Security (30 points)
        score += analysis.get('security_score', 0) * 0.3
        
        # Mobile (25 points)
        score += analysis.get('mobile_score', 0) * 0.25
        
        # Structure (20 points)
        score += analysis.get('structure_score', 0) * 0.2
        
        # Technical elements (25 points)
        if analysis.get('has_viewport'):
            score += 5
        if analysis.get('canonical_url'):
            score += 5
        if analysis.get('schema_count', 0) > 0:
            score += 5
        if analysis.get('has_sitemap_link'):
            score += 5
        if analysis.get('language'):
            score += 5
        
        return min(100, int(score))
    
    def _deep_compare_results(self, result1: Dict, result2: Dict) -> Dict:
        """Perform deep comparison between two results."""
        comparison = {
            'performance': {
                'load_time': {
                    'your_site': result1.get('load_time', 0),
                    'competitor': result2.get('load_time', 0),
                    'winner': 'your_site' if result1.get('load_time', 999) < result2.get('load_time', 999) else 'competitor',
                    'difference': abs(result1.get('load_time', 0) - result2.get('load_time', 0))
                },
                'page_size': {
                    'your_site': result1.get('page_size', 0),
                    'competitor': result2.get('page_size', 0),
                    'winner': 'your_site' if result1.get('page_size', 999999) < result2.get('page_size', 999999) else 'competitor'
                },
                'performance_score': {
                    'your_site': result1.get('performance_score', 0),
                    'competitor': result2.get('performance_score', 0),
                    'winner': 'your_site' if result1.get('performance_score', 0) > result2.get('performance_score', 0) else 'competitor'
                }
            },
            'seo': {
                'seo_score': {
                    'your_site': result1.get('seo_score', 0),
                    'competitor': result2.get('seo_score', 0),
                    'difference': result1.get('seo_score', 0) - result2.get('seo_score', 0),
                    'winner': 'your_site' if result1.get('seo_score', 0) > result2.get('seo_score', 0) else 'competitor'
                },
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
                    'h1': {
                        'your_site': result1.get('h1_count', 0),
                        'competitor': result2.get('h1_count', 0)
                    },
                    'h2': {
                        'your_site': result1.get('h2_count', 0),
                        'competitor': result2.get('h2_count', 0)
                    }
                },
                'word_count': {
                    'your_site': result1.get('word_count', 0),
                    'competitor': result2.get('word_count', 0),
                    'difference': result1.get('word_count', 0) - result2.get('word_count', 0)
                },
                'images': {
                    'your_site': {
                        'total': result1.get('images_count', 0),
                        'with_alt': result1.get('images_with_alt', 0),
                        'alt_coverage': result1.get('images_alt_coverage', 0)
                    },
                    'competitor': {
                        'total': result2.get('images_count', 0),
                        'with_alt': result2.get('images_with_alt', 0),
                        'alt_coverage': result2.get('images_alt_coverage', 0)
                    }
                }
            },
            'technical': {
                'technical_score': {
                    'your_site': result1.get('technical_score', 0),
                    'competitor': result2.get('technical_score', 0),
                    'winner': 'your_site' if result1.get('technical_score', 0) > result2.get('technical_score', 0) else 'competitor'
                },
                'mobile': {
                    'your_site': result1.get('mobile_score', 0),
                    'competitor': result2.get('mobile_score', 0)
                },
                'security': {
                    'your_site': result1.get('security_score', 0),
                    'competitor': result2.get('security_score', 0)
                },
                'schema': {
                    'your_site': result1.get('schema_count', 0),
                    'competitor': result2.get('schema_count', 0)
                }
            },
            'keywords': {
                'common_keywords': self._find_common_keywords_advanced(
                    result1.get('keywords', []),
                    result2.get('keywords', [])
                ),
                'unique_to_your_site': self._find_unique_keywords_advanced(
                    result1.get('keywords', []),
                    result2.get('keywords', [])
                ),
                'unique_to_competitor': self._find_unique_keywords_advanced(
                    result2.get('keywords', []),
                    result1.get('keywords', [])
                ),
                'keyword_diversity': {
                    'your_site': result1.get('keyword_diversity', 0),
                    'competitor': result2.get('keyword_diversity', 0)
                }
            },
            'backlinks': {
                'your_site': result1.get('backlink_indicators', {}),
                'competitor': result2.get('backlink_indicators', {})
            },
            'content_quality': {
                'readability': {
                    'your_site': result1.get('readability_score', 0),
                    'competitor': result2.get('readability_score', 0)
                },
                'content_density': {
                    'your_site': result1.get('content_density', {}).get('content_ratio', 0) if isinstance(result1.get('content_density'), dict) else 0,
                    'competitor': result2.get('content_density', {}).get('content_ratio', 0) if isinstance(result2.get('content_density'), dict) else 0
                }
            }
        }
        
        return comparison
    
    def _find_common_keywords_advanced(self, keywords1: List[Tuple], keywords2: List[Tuple]) -> List[Dict]:
        """Find common keywords with advanced analysis."""
        words1 = {word: (count, importance) for word, count, importance in keywords1}
        words2 = {word: (count, importance) for word, count, importance in keywords2}
        
        common = []
        for word in set(words1.keys()) & set(words2.keys()):
            count1, imp1 = words1[word]
            count2, imp2 = words2[word]
            common.append({
                'keyword': word,
                'your_count': count1,
                'competitor_count': count2,
                'your_importance': round(imp1, 4),
                'competitor_importance': round(imp2, 4),
                'total_count': count1 + count2,
                'total_importance': round(imp1 + imp2, 4)
            })
        
        common.sort(key=lambda x: x['total_importance'], reverse=True)
        return common[:30]  # Top 30
    
    def _find_unique_keywords_advanced(self, keywords1: List[Tuple], keywords2: List[Tuple]) -> List[Dict]:
        """Find unique keywords with importance scores."""
        words1 = {word: (count, importance) for word, count, importance in keywords1}
        words2 = {word: (count, importance) for word, count, importance in keywords2}
        
        unique = []
        for word, (count, importance) in words1.items():
            if word not in words2:
                unique.append({
                    'keyword': word,
                    'count': count,
                    'importance': round(importance, 4)
                })
        
        unique.sort(key=lambda x: x['importance'], reverse=True)
        return unique[:30]  # Top 30
    
    def _calculate_advantage_score(self, comparison: Dict, result1: Dict, result2: Dict) -> Dict:
        """Calculate competitive advantage score."""
        your_wins = 0
        competitor_wins = 0
        ties = 0
        
        categories = []
        
        # Performance
        if comparison['performance']['load_time']['winner'] == 'your_site':
            your_wins += 1
            categories.append('Load Speed')
        elif comparison['performance']['load_time']['winner'] == 'competitor':
            competitor_wins += 1
        
        if comparison['performance']['performance_score']['winner'] == 'your_site':
            your_wins += 1
            categories.append('Performance Score')
        elif comparison['performance']['performance_score']['winner'] == 'competitor':
            competitor_wins += 1
        
        # SEO
        if comparison['seo']['seo_score']['winner'] == 'your_site':
            your_wins += 1
            categories.append('SEO Score')
        elif comparison['seo']['seo_score']['winner'] == 'competitor':
            competitor_wins += 1
        
        # Technical
        if comparison['technical']['technical_score']['winner'] == 'your_site':
            your_wins += 1
            categories.append('Technical SEO')
        elif comparison['technical']['technical_score']['winner'] == 'competitor':
            competitor_wins += 1
        
        # Mobile
        if comparison['technical']['mobile']['your_site'] > comparison['technical']['mobile']['competitor']:
            your_wins += 1
            categories.append('Mobile-Friendliness')
        elif comparison['technical']['mobile']['competitor'] > comparison['technical']['mobile']['your_site']:
            competitor_wins += 1
        
        # Security
        if comparison['technical']['security']['your_site'] > comparison['technical']['security']['competitor']:
            your_wins += 1
            categories.append('Security')
        elif comparison['technical']['security']['competitor'] > comparison['technical']['security']['your_site']:
            competitor_wins += 1
        
        total_categories = your_wins + competitor_wins + ties
        advantage_percentage = (your_wins / total_categories * 100) if total_categories > 0 else 0
        
        return {
            'your_wins': your_wins,
            'competitor_wins': competitor_wins,
            'ties': ties,
            'total_categories': total_categories,
            'advantage_percentage': round(advantage_percentage, 1),
            'winning_categories': categories,
            'advantage_level': self._get_advantage_level(advantage_percentage)
        }
    
    def _get_advantage_level(self, percentage: float) -> str:
        """Get advantage level description."""
        if percentage >= 70:
            return 'Strong Advantage'
        elif percentage >= 50:
            return 'Moderate Advantage'
        elif percentage >= 30:
            return 'Slight Advantage'
        else:
            return 'Competitive Disadvantage'
    
    def _determine_winner_advanced(self, comparison: Dict, advantage: Dict) -> Dict:
        """Determine overall winner with detailed breakdown."""
        overall_winner = 'your_site' if advantage['your_wins'] > advantage['competitor_wins'] else \
                        'competitor' if advantage['competitor_wins'] > advantage['your_wins'] else 'tie'
        
        return {
            'overall': overall_winner,
            'advantage_score': advantage['advantage_percentage'],
            'advantage_level': advantage['advantage_level'],
            'wins': {
                'your_site': advantage['your_wins'],
                'competitor': advantage['competitor_wins'],
                'ties': advantage['ties']
            },
            'winning_categories': advantage['winning_categories'],
            'summary': f"Your site wins {advantage['your_wins']} categories, competitor wins {advantage['competitor_wins']} categories"
        }
    
    def _generate_advanced_insights(self, comparison: Dict, result1: Dict, result2: Dict) -> List[str]:
        """Generate advanced actionable insights."""
        insights = []
        
        # Performance insights
        load_diff = comparison['performance']['load_time']['difference']
        if comparison['performance']['load_time']['winner'] == 'competitor' and load_diff > 1:
            insights.append(f"🚨 CRITICAL: Competitor loads {load_diff:.2f}s faster - This significantly impacts user experience and SEO")
        elif comparison['performance']['load_time']['winner'] == 'your_site' and load_diff > 1:
            insights.append(f"✅ EXCELLENT: Your site loads {load_diff:.2f}s faster - Great performance advantage")
        
        # SEO insights
        seo_diff = comparison['seo']['seo_score']['difference']
        if seo_diff < -15:
            insights.append(f"⚠️ WARNING: Competitor has {abs(seo_diff)} points higher SEO score - Major gap to address")
        elif seo_diff > 15:
            insights.append(f"✅ STRONG: Your site has {seo_diff} points higher SEO score - Excellent on-page optimization")
        
        # Content insights
        word_diff = comparison['seo']['word_count']['difference']
        if word_diff < -500:
            insights.append(f"💡 OPPORTUNITY: Competitor has {abs(word_diff)} more words - Consider expanding content depth")
        elif word_diff > 500:
            insights.append(f"✅ ADVANTAGE: Your site has {word_diff} more words - Better content depth")
        
        # Keyword insights
        unique_yours = len(comparison['keywords']['unique_to_your_site'])
        unique_comp = len(comparison['keywords']['unique_to_competitor'])
        if unique_comp > unique_yours * 1.5:
            insights.append(f"🔍 RESEARCH: Competitor uses {unique_comp - unique_yours} more unique keywords - Research their keyword strategy")
        
        # Technical insights
        tech_diff = comparison['technical']['technical_score']['your_site'] - comparison['technical']['technical_score']['competitor']
        if tech_diff < -20:
            insights.append(f"🔧 TECHNICAL: Competitor has better technical SEO - Improve mobile, security, and structure")
        
        # Mobile insights
        mobile_diff = comparison['technical']['mobile']['competitor'] - comparison['technical']['mobile']['your_site']
        if mobile_diff > 20:
            insights.append(f"📱 MOBILE: Competitor is more mobile-friendly - Optimize viewport and responsive design")
        
        # Security insights
        sec_diff = comparison['technical']['security']['competitor'] - comparison['technical']['security']['your_site']
        if sec_diff > 15:
            insights.append(f"🔒 SECURITY: Competitor has better security headers - Implement security best practices")
        
        return insights
    
    def _generate_recommendations(self, comparison: Dict, result1: Dict, result2: Dict) -> List[Dict]:
        """Generate specific recommendations."""
        recommendations = []
        
        # Title recommendations
        your_title_len = comparison['seo']['title']['your_length']
        comp_title_len = comparison['seo']['title']['competitor_length']
        if comp_title_len > your_title_len and 30 <= comp_title_len <= 60:
            recommendations.append({
                'category': 'Title Tag',
                'priority': 'high',
                'action': f'Expand title from {your_title_len} to {comp_title_len} characters',
                'reason': 'Competitor uses optimal title length for better SEO'
            })
        
        # Meta description recommendations
        your_desc_len = comparison['seo']['meta_description']['your_length']
        comp_desc_len = comparison['seo']['meta_description']['competitor_length']
        if comp_desc_len > your_desc_len and 120 <= comp_desc_len <= 160:
            recommendations.append({
                'category': 'Meta Description',
                'priority': 'medium',
                'action': f'Expand meta description from {your_desc_len} to {comp_desc_len} characters',
                'reason': 'Competitor uses optimal description length'
            })
        
        # Content recommendations
        word_diff = comparison['seo']['word_count']['difference']
        if word_diff < -300:
            recommendations.append({
                'category': 'Content',
                'priority': 'high',
                'action': f'Add {abs(word_diff)}+ words to match competitor content depth',
                'reason': 'More content typically ranks better'
            })
        
        # Image alt tags
        your_alt = comparison['seo']['images']['your_site']['alt_coverage']
        comp_alt = comparison['seo']['images']['competitor']['alt_coverage']
        if comp_alt > your_alt + 10:
            recommendations.append({
                'category': 'Images',
                'priority': 'medium',
                'action': f'Improve image alt tag coverage from {your_alt}% to {comp_alt}%',
                'reason': 'Better alt tag coverage improves SEO and accessibility'
            })
        
        # Performance recommendations
        if comparison['performance']['load_time']['winner'] == 'competitor':
            recommendations.append({
                'category': 'Performance',
                'priority': 'critical',
                'action': 'Optimize page load speed - compress images, minify CSS/JS, use CDN',
                'reason': 'Faster load times improve user experience and rankings'
            })
        
        # Mobile recommendations
        if comparison['technical']['mobile']['competitor'] > comparison['technical']['mobile']['your_site'] + 20:
            recommendations.append({
                'category': 'Mobile',
                'priority': 'high',
                'action': 'Improve mobile-friendliness - add viewport meta, optimize for mobile',
                'reason': 'Mobile-first indexing makes this critical'
            })
        
        return recommendations

