"""
Render & Loading Issues Analyzer.

Detects:
- Render-blocking CSS and JS
- Above-the-fold content delay detection
- Lazy-load misuse detection
- Critical CSS missing detection
"""
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag


class RenderLoadingAnalyzer:
    """
    Analyzes render-blocking resources and loading issues.
    """
    
    def analyze_page(self, html_content: str, page_url: str) -> Dict:
        """
        Analyze page for render and loading issues.
        
        Args:
            html_content: HTML content of the page
            page_url: Base URL of the page
            
        Returns:
            Dictionary with render/loading analysis results
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        results = {
            'render_blocking_resources': self._detect_render_blocking(soup, page_url),
            'above_fold_delays': self._detect_above_fold_delays(soup, page_url),
            'lazy_load_issues': self._detect_lazy_load_issues(soup),
            'critical_css_issues': self._detect_critical_css_issues(soup),
            'font_loading_issues': self._detect_font_loading_issues(soup),
            'summary': {}
        }
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _detect_render_blocking(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """
        Detect render-blocking CSS and JS resources.
        
        Returns:
            Dictionary with render-blocking resource analysis
        """
        blocking_css = []
        blocking_js = []
        
        # Find CSS links in <head> (blocking by default)
        head = soup.find('head')
        if head:
            css_links = head.find_all('link', rel='stylesheet')
            for link in css_links:
                href = link.get('href', '')
                media = link.get('media', 'all')
                
                # CSS is render-blocking unless it has media="print" or is preloaded
                is_blocking = True
                if media and media.lower() == 'print':
                    is_blocking = False
                
                rel = link.get('rel', [])
                if isinstance(rel, list) and 'preload' in rel:
                    is_blocking = False  # Preloaded resources don't block
                
                if is_blocking:
                    blocking_css.append({
                        'url': urljoin(base_url, href) if href else '',
                        'media': media,
                        'type': 'stylesheet',
                        'recommendation': 'Consider inlining critical CSS or using media="print" for non-critical stylesheets'
                    })
        
        # Find blocking JavaScript in <head> (scripts without async/defer)
        scripts = soup.find_all('script')
        for script in scripts:
            src = script.get('src', '')
            async_attr = script.get('async')
            defer_attr = script.get('defer')
            type_attr = script.get('type', '').lower()
            
            # Skip module scripts (they're async by default)
            if 'module' in type_attr:
                continue
            
            # Script is blocking if it's in head and has no async/defer
            is_blocking = False
            if src:
                # Check if script is in head (approximation: if it's before body)
                body = soup.find('body')
                if body:
                    script_index = html_content.find(str(script))
                    body_index = html_content.find('<body')
                    if script_index < body_index or body_index == -1:
                        is_blocking = async_attr is None and defer_attr is None
                else:
                    # No body tag, assume it's in head
                    is_blocking = async_attr is None and defer_attr is None
                
                if is_blocking:
                    blocking_js.append({
                        'url': urljoin(base_url, src) if src else '',
                        'async': async_attr is not None,
                        'defer': defer_attr is not None,
                        'type': 'external',
                        'recommendation': 'Add async or defer attribute to prevent render blocking'
                    })
        
        return {
            'css': blocking_css,
            'javascript': blocking_js,
            'total_blocking_resources': len(blocking_css) + len(blocking_js),
            'severity': 'critical' if len(blocking_css) + len(blocking_js) > 5 else 'warning'
        }
    
    def _detect_above_fold_delays(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Detect resources that delay above-the-fold content.
        
        Returns:
            List of resources causing above-fold delays
        """
        delays = []
        
        # Find large images that appear early in HTML (likely above fold)
        images = soup.find_all('img', limit=10)  # Check first 10 images
        for img in images[:5]:  # Focus on first 5
            src = img.get('src') or img.get('data-src', '')
            loading = img.get('loading', '').lower()
            
            # If image is early in HTML and not lazy-loaded, it may delay above-fold
            if src and loading != 'lazy':
                delays.append({
                    'type': 'image',
                    'element': 'img',
                    'src': urljoin(base_url, src) if src else '',
                    'issue': 'Image in early HTML without lazy-loading may delay above-fold content',
                    'recommendation': 'Consider lazy-loading images below the fold'
                })
        
        # Check for external CSS loaded before body (delays rendering)
        head = soup.find('head')
        if head:
            css_links = head.find_all('link', rel='stylesheet')
            if len(css_links) > 3:
                delays.append({
                    'type': 'stylesheet',
                    'issue': f'{len(css_links)} stylesheets in <head> may delay above-fold rendering',
                    'recommendation': 'Inline critical CSS and defer non-critical stylesheets'
                })
        
        # Check for blocking scripts before body
        body = soup.find('body')
        if body:
            body_start = html_content.find('<body')
            scripts_before_body = []
            for script in soup.find_all('script', src=True):
                script_str = str(script)
                script_pos = html_content.find(script_str)
                if script_pos < body_start and script_pos > 0:
                    async_attr = script.get('async')
                    defer_attr = script.get('defer')
                    if async_attr is None and defer_attr is None:
                        scripts_before_body.append(script.get('src', ''))
            
            if scripts_before_body:
                delays.append({
                    'type': 'javascript',
                    'issue': f'{len(scripts_before_body)} blocking scripts before <body> delay rendering',
                    'scripts': scripts_before_body[:5],
                    'recommendation': 'Move scripts to end of body or use async/defer'
                })
        
        return delays
    
    def _detect_lazy_load_issues(self, soup: BeautifulSoup) -> Dict:
        """
        Detect lazy-loading misuse (images that should/shouldn't be lazy-loaded).
        
        Returns:
            Dictionary with lazy-load issues
        """
        issues = []
        
        images = soup.find_all('img')
        total_images = len(images)
        lazy_loaded = 0
        above_fold_lazy = []  # Images that are lazy-loaded but should be immediate
        below_fold_immediate = []  # Images that should be lazy-loaded but aren't
        
        # Heuristic: First 3 images are likely above fold
        above_fold_threshold = min(3, total_images)
        
        for i, img in enumerate(images):
            src = img.get('src') or img.get('data-src', '')
            loading = img.get('loading', '').lower()
            is_lazy = loading == 'lazy'
            
            if is_lazy:
                lazy_loaded += 1
            
            # Check if above-fold image is lazy-loaded (bad)
            if i < above_fold_threshold and is_lazy:
                above_fold_lazy.append({
                    'image': src or 'unknown',
                    'position': i + 1,
                    'issue': 'Above-fold image is lazy-loaded, causing delayed display',
                    'recommendation': 'Remove lazy-loading from above-fold images'
                })
            
            # Check if below-fold image is not lazy-loaded (potential improvement)
            if i >= above_fold_threshold and not is_lazy and src:
                below_fold_immediate.append({
                    'image': src,
                    'position': i + 1,
                    'issue': 'Below-fold image is not lazy-loaded',
                    'recommendation': 'Add loading="lazy" to improve initial page load'
                })
        
        # Check for iframe lazy-loading
        iframes = soup.find_all('iframe')
        iframe_lazy_loaded = sum(1 for iframe in iframes if iframe.get('loading', '').lower() == 'lazy')
        
        return {
            'total_images': total_images,
            'lazy_loaded_images': lazy_loaded,
            'above_fold_lazy_loaded': above_fold_lazy,
            'below_fold_not_lazy': below_fold_immediate,
            'iframe_lazy_count': iframe_lazy_loaded,
            'total_iframes': len(iframes),
            'recommendations': self._generate_lazy_load_recommendations(
                above_fold_lazy, below_fold_immediate, lazy_loaded, total_images
            )
        }
    
    def _detect_critical_css_issues(self, soup: BeautifulSoup) -> Dict:
        """
        Detect critical CSS missing or excessive CSS.
        
        Returns:
            Dictionary with critical CSS analysis
        """
        issues = []
        
        # Check for inline critical CSS
        head = soup.find('head')
        has_inline_critical = False
        if head:
            style_tags = head.find_all('style')
            if style_tags:
                has_inline_critical = True
        
        # Count external stylesheets
        external_css = soup.find_all('link', rel='stylesheet')
        external_count = len(external_css)
        
        # Check for large CSS files (indicating lack of critical CSS extraction)
        if external_count > 3 and not has_inline_critical:
            issues.append({
                'type': 'no_critical_css',
                'issue': 'Multiple external stylesheets without inline critical CSS',
                'external_count': external_count,
                'recommendation': 'Inline critical CSS and defer non-critical stylesheets to improve above-fold rendering'
            })
        
        # Check for preload of CSS
        preloaded_css = soup.find_all('link', rel='preload', as_='style')
        if preloaded_css and not has_inline_critical:
            issues.append({
                'type': 'css_preload_without_inline',
                'issue': 'CSS is preloaded but no critical CSS is inlined',
                'recommendation': 'Consider inlining critical CSS for faster initial render'
            })
        
        return {
            'has_inline_critical_css': has_inline_critical,
            'external_stylesheet_count': external_count,
            'preloaded_css_count': len(preloaded_css),
            'issues': issues,
            'score': 'good' if has_inline_critical or external_count <= 2 else 'needs-improvement'
        }
    
    def _detect_font_loading_issues(self, soup: BeautifulSoup) -> Dict:
        """Detect font loading issues."""
        issues = []
        
        # Check for font-display in @font-face
        style_tags = soup.find_all('style')
        font_faces_without_display = 0
        
        for style in style_tags:
            style_content = style.string or ''
            if '@font-face' in style_content:
                font_face_blocks = re.findall(r'@font-face\s*\{[^}]*\}', style_content, re.IGNORECASE)
                for block in font_face_blocks:
                    if 'font-display' not in block.lower():
                        font_faces_without_display += 1
        
        if font_faces_without_display > 0:
            issues.append({
                'type': 'missing_font_display',
                'count': font_faces_without_display,
                'issue': f'{font_faces_without_display} @font-face declarations without font-display property',
                'recommendation': 'Add font-display: swap or optional to prevent FOIT (Flash of Invisible Text)'
            })
        
        # Check for font preloading
        font_preloads = soup.find_all('link', rel='preload', as_='font')
        
        return {
            'font_faces_without_display': font_faces_without_display,
            'font_preloads': len(font_preloads),
            'issues': issues
        }
    
    def _generate_lazy_load_recommendations(self, above_fold_lazy: List, below_fold_not_lazy: List, 
                                           lazy_count: int, total: int) -> List[str]:
        """Generate lazy-load recommendations."""
        recommendations = []
        
        if above_fold_lazy:
            recommendations.append(f'Remove lazy-loading from {len(above_fold_lazy)} above-fold images')
        
        if below_fold_not_lazy:
            recommendations.append(f'Add lazy-loading to {len(below_fold_not_lazy)} below-fold images to improve initial load')
        
        lazy_percentage = (lazy_count / total * 100) if total > 0 else 0
        if lazy_percentage < 50 and total > 5:
            recommendations.append(f'Only {lazy_percentage:.0f}% of images are lazy-loaded. Consider lazy-loading more below-fold images')
        
        return recommendations
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate summary of render/loading issues."""
        blocking = results.get('render_blocking_resources', {})
        lazy_load = results.get('lazy_load_issues', {})
        critical_css = results.get('critical_css_issues', {})
        
        total_issues = (
            len(blocking.get('css', [])) + len(blocking.get('javascript', [])) +
            len(results.get('above_fold_delays', [])) +
            len(lazy_load.get('above_fold_lazy_loaded', [])) +
            len(critical_css.get('issues', []))
        )
        
        return {
            'total_issues': total_issues,
            'blocking_resources': blocking.get('total_blocking_resources', 0),
            'critical_issues': len([r for r in results.get('above_fold_delays', []) if r.get('type') in ['stylesheet', 'javascript']]),
            'score': self._calculate_score(total_issues, blocking.get('total_blocking_resources', 0))
        }
    
    @staticmethod
    def _calculate_score(total_issues: int, blocking_resources: int) -> str:
        """Calculate overall score."""
        if total_issues == 0 and blocking_resources <= 2:
            return 'good'
        elif total_issues <= 3 and blocking_resources <= 5:
            return 'needs-improvement'
        else:
            return 'poor'

