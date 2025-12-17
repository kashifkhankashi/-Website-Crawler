"""
Core Web Vitals Analyzer using Playwright for field-style simulation.

Measures:
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)
- Interaction to Next Paint (INP) / First Input Delay (FID)
- Time to First Byte (TTFB)

Detects:
- Large elements contributing to LCP
- Layout shift causes (images without dimensions, ads, dynamic content)
"""
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class CoreWebVitalsAnalyzer:
    """
    Analyzes Core Web Vitals using Playwright for browser-based measurements.
    """
    
    def __init__(self, timeout: int = 30000, headless: bool = True):
        """
        Initialize the analyzer.
        
        Args:
            timeout: Maximum time to wait for page load (ms)
            headless: Run browser in headless mode
        """
        self.timeout = timeout
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._playwright = None
        
    async def _init_browser(self):
        """Initialize Playwright browser (lazy initialization)."""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Install with: pip install playwright && playwright install")
        
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
    
    async def _close_browser(self):
        """Close browser and cleanup."""
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
    
    async def analyze_page(self, url: str, html_content: Optional[str] = None) -> Dict:
        """
        Analyze Core Web Vitals for a page.
        
        Args:
            url: URL to analyze
            html_content: Optional HTML content (if None, will fetch from URL)
            
        Returns:
            Dictionary with Core Web Vitals metrics and issues
        """
        if not PLAYWRIGHT_AVAILABLE:
            return self._get_unavailable_response()
        
        try:
            await self._init_browser()
            
            page = await self.context.new_page()
            
            # Set up metrics collection
            metrics = {
                'lcp': None,
                'cls': 0.0,
                'inp': None,
                'fid': None,
                'ttfb': None,
                'fcp': None,
                'lcp_element': None,
                'layout_shifts': [],
                'lcp_issues': [],
                'cls_issues': []
            }
            
            # Collect layout shifts
            layout_shifts = []
            
            def handle_layout_shift(entries):
                for entry in entries:
                    if entry.get('hadRecentInput'):
                        continue
                    value = entry.get('value', 0)
                    layout_shifts.append({
                        'value': value,
                        'sources': entry.get('sources', []),
                        'startTime': entry.get('startTime', 0)
                    })
            
            # Listen to performance metrics
            async def collect_metrics():
                try:
                    # Wait for page to be interactive
                    await page.wait_for_load_state('networkidle', timeout=self.timeout)
                    await page.wait_for_timeout(2000)  # Additional wait for layout stability
                    
                    # Get LCP
                    lcp_metric = await page.evaluate("""() => {
                        return new Promise((resolve) => {
                            if (!window.performance || !window.performance.getEntriesByType) {
                                resolve(null);
                                return;
                            }
                            
                            const entries = performance.getEntriesByType('largest-contentful-paint');
                            if (entries.length > 0) {
                                const lastEntry = entries[entries.length - 1];
                                resolve({
                                    value: lastEntry.renderTime || lastEntry.loadTime,
                                    element: lastEntry.element ? {
                                        tagName: lastEntry.element.tagName,
                                        src: lastEntry.element.src || lastEntry.element.currentSrc || '',
                                        text: lastEntry.element.textContent?.substring(0, 100) || ''
                                    } : null
                                });
                            } else {
                                resolve(null);
                            }
                        });
                    }""")
                    
                    if lcp_metric:
                        metrics['lcp'] = lcp_metric.get('value', 0) / 1000  # Convert to seconds
                        metrics['lcp_element'] = lcp_metric.get('element')
                    
                    # Get CLS (sum of layout shifts)
                    cls_value = sum(ls['value'] for ls in layout_shifts)
                    metrics['cls'] = cls_value
                    metrics['layout_shifts'] = layout_shifts
                    
                    # Get FCP
                    fcp_entries = await page.evaluate("""() => {
                        const entries = performance.getEntriesByType('paint');
                        for (const entry of entries) {
                            if (entry.name === 'first-contentful-paint') {
                                return entry.startTime;
                            }
                        }
                        return null;
                    }""")
                    if fcp_entries:
                        metrics['fcp'] = fcp_entries / 1000  # Convert to seconds
                    
                    # Get TTFB
                    nav_timing = await page.evaluate("""() => {
                        if (window.performance && window.performance.timing) {
                            const timing = window.performance.timing;
                            return timing.responseStart - timing.requestStart;
                        }
                        return null;
                    }""")
                    if nav_timing:
                        metrics['ttfb'] = nav_timing / 1000  # Convert to seconds
                    
                    # Simulate INP by measuring response time to click
                    try:
                        start_time = time.time()
                        await page.mouse.click(100, 100)
                        await page.wait_for_timeout(100)
                        inp_value = (time.time() - start_time) * 1000  # Convert to ms
                        metrics['inp'] = inp_value
                    except:
                        pass
                    
                except Exception as e:
                    print(f"Warning: Error collecting metrics: {e}")
            
            # Navigate and collect metrics
            try:
                if html_content:
                    # Set content directly
                    await page.set_content(html_content, wait_until='networkidle')
                else:
                    # Navigate to URL
                    response = await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
                    metrics['ttfb'] = (response.request.timing.get('responseStart', 0) - response.request.timing.get('requestStart', 0)) / 1000
                
                # Set up layout shift observer
                await page.add_init_script("""
                    if ('PerformanceObserver' in window) {
                        try {
                            const observer = new PerformanceObserver((list) => {
                                window._layoutShifts = window._layoutShifts || [];
                                for (const entry of list.getEntries()) {
                                    if (!entry.hadRecentInput) {
                                        window._layoutShifts.push({
                                            value: entry.value,
                                            sources: entry.sources.map(s => ({
                                                node: s.node ? s.node.tagName : null,
                                                previousRect: s.previousRect,
                                                currentRect: s.currentRect
                                            })),
                                            startTime: entry.startTime
                                        });
                                    }
                                }
                            });
                            observer.observe({ entryTypes: ['layout-shift'] });
                        } catch (e) {}
                    }
                """)
                
                await collect_metrics()
                
                # Analyze HTML for LCP and CLS issues
                html_content_for_analysis = await page.content()
                lcp_issues, cls_issues = self._analyze_html_for_issues(html_content_for_analysis, url)
                metrics['lcp_issues'] = lcp_issues
                metrics['cls_issues'] = cls_issues
                
            except Exception as e:
                print(f"Warning: Error analyzing page {url}: {e}")
                metrics['error'] = str(e)
            
            finally:
                await page.close()
            
            # Calculate scores
            metrics['lcp_score'] = self._score_lcp(metrics.get('lcp'))
            metrics['cls_score'] = self._score_cls(metrics.get('cls'))
            metrics['inp_score'] = self._score_inp(metrics.get('inp'))
            metrics['ttfb_score'] = self._score_ttfb(metrics.get('ttfb'))
            
            return metrics
            
        except Exception as e:
            return {
                'error': str(e),
                'lcp': None,
                'cls': 0.0,
                'inp': None,
                'ttfb': None
            }
    
    def _analyze_html_for_issues(self, html_content: str, base_url: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Analyze HTML to detect potential LCP and CLS issues.
        
        Returns:
            Tuple of (lcp_issues, cls_issues)
        """
        lcp_issues = []
        cls_issues = []
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # LCP Issues: Large images without dimensions
            images = soup.find_all('img')
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src', '')
                width = img.get('width')
                height = img.get('height')
                
                # Check if image is likely LCP candidate (large, above fold)
                if src and not width and not height:
                    lcp_issues.append({
                        'type': 'image_without_dimensions',
                        'element': 'img',
                        'src': src,
                        'issue': 'Image missing width/height attributes can cause layout shift and delay LCP',
                        'recommendation': 'Add width and height attributes to image tags'
                    })
            
            # CLS Issues: Images, ads, embeds without dimensions
            for img in images:
                src = img.get('src') or img.get('data-src', '')
                width = img.get('width')
                height = img.get('height')
                style = img.get('style', '')
                
                if src and not width and not height and 'aspect-ratio' not in style:
                    cls_issues.append({
                        'type': 'image_without_dimensions',
                        'element': 'img',
                        'src': src,
                        'issue': 'Image without dimensions can cause layout shift when loaded',
                        'recommendation': 'Add width, height, or aspect-ratio CSS to prevent layout shift'
                    })
            
            # CLS Issues: Dynamic content injection
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.string or ''
                # Detect common patterns that inject content
                if any(pattern in script_content.lower() for pattern in ['innerhtml', 'appendchild', 'insertadjacenthtml']):
                    cls_issues.append({
                        'type': 'dynamic_content_injection',
                        'element': 'script',
                        'issue': 'JavaScript dynamically injects content which can cause layout shifts',
                        'recommendation': 'Reserve space for dynamically injected content or use CSS to prevent layout shift'
                    })
            
            # CLS Issues: Ads without reserved space
            ad_selectors = ['iframe[src*="ads"]', 'div[class*="ad"]', 'div[id*="ad"]']
            for selector_pattern in ad_selectors:
                try:
                    ads = soup.select(selector_pattern)
                    for ad in ads:
                        style = ad.get('style', '')
                        if 'height' not in style and not ad.get('height'):
                            cls_issues.append({
                                'type': 'ad_without_dimensions',
                                'element': ad.name,
                                'issue': 'Advertisement container without fixed dimensions can cause layout shift',
                                'recommendation': 'Reserve space for ads to prevent layout shift'
                            })
                except:
                    pass
            
            # CLS Issues: Fonts without font-display
            stylesheets = soup.find_all(['style', 'link'], rel='stylesheet')
            for stylesheet in stylesheets:
                content = stylesheet.string or ''
                href = stylesheet.get('href', '')
                if 'font-display' not in content and ('font' in href.lower() or 'font-face' in content.lower()):
                    cls_issues.append({
                        'type': 'font_without_display',
                        'issue': 'Web fonts without font-display can cause FOIT/FOUT and layout shifts',
                        'recommendation': 'Add font-display: swap or optional to @font-face declarations'
                    })
            
        except Exception as e:
            print(f"Warning: Error analyzing HTML for issues: {e}")
        
        return lcp_issues, cls_issues
    
    @staticmethod
    def _score_lcp(lcp_value: Optional[float]) -> Optional[str]:
        """Score LCP value (good/poor/needs-improvement)."""
        if lcp_value is None:
            return None
        if lcp_value <= 2.5:
            return 'good'
        elif lcp_value <= 4.0:
            return 'needs-improvement'
        else:
            return 'poor'
    
    @staticmethod
    def _score_cls(cls_value: float) -> str:
        """Score CLS value."""
        if cls_value <= 0.1:
            return 'good'
        elif cls_value <= 0.25:
            return 'needs-improvement'
        else:
            return 'poor'
    
    @staticmethod
    def _score_inp(inp_value: Optional[float]) -> Optional[str]:
        """Score INP value (in milliseconds)."""
        if inp_value is None:
            return None
        if inp_value <= 200:
            return 'good'
        elif inp_value <= 500:
            return 'needs-improvement'
        else:
            return 'poor'
    
    @staticmethod
    def _score_ttfb(ttfb_value: Optional[float]) -> Optional[str]:
        """Score TTFB value."""
        if ttfb_value is None:
            return None
        if ttfb_value <= 0.8:
            return 'good'
        elif ttfb_value <= 1.8:
            return 'needs-improvement'
        else:
            return 'poor'
    
    @staticmethod
    def _get_unavailable_response() -> Dict:
        """Return response when Playwright is not available."""
        return {
            'error': 'Playwright not available',
            'lcp': None,
            'cls': 0.0,
            'inp': None,
            'ttfb': None,
            'message': 'Install Playwright with: pip install playwright && playwright install'
        }
    
    def analyze_page_sync(self, url: str, html_content: Optional[str] = None) -> Dict:
        """
        Synchronous wrapper for analyze_page (for compatibility).
        
        Args:
            url: URL to analyze
            html_content: Optional HTML content
            
        Returns:
            Dictionary with Core Web Vitals metrics
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.analyze_page(url, html_content))
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            if self.context or self.browser or self._playwright:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Can't close in running loop, will be cleaned up by garbage collector
                    pass
                else:
                    loop.run_until_complete(self._close_browser())
        except:
            pass

