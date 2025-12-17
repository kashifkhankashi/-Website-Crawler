"""
Advanced SEO Audit Orchestrator.

Orchestrates all advanced SEO analyzers with feature flags.
This module integrates all new analyzers while maintaining backward compatibility.
"""
from typing import Dict, List, Optional
import asyncio


class AdvancedSEOAuditOrchestrator:
    """
    Orchestrates all advanced SEO audit analyzers.
    """
    
    def __init__(self, analysis_config: Optional[Dict] = None):
        """
        Initialize orchestrator with feature flags.
        
        Args:
            analysis_config: Dictionary with feature flags for analyzers
        """
        self.analysis_config = analysis_config or {}
        
        # Default feature flags (all enabled by default)
        self.feature_flags = {
            'core_web_vitals': self.analysis_config.get('enable_core_web_vitals', True),
            'advanced_performance': self.analysis_config.get('enable_advanced_performance', True),
            'render_loading': self.analysis_config.get('enable_render_loading_analysis', True),
            'indexability': self.analysis_config.get('enable_indexability_analysis', True),
            'security': self.analysis_config.get('enable_security_analysis', True),
            'comprehensive_scoring': self.analysis_config.get('enable_comprehensive_scoring', True),
            'use_playwright_for_cwv': self.analysis_config.get('use_playwright_for_cwv', False),  # Off by default (expensive)
        }
        
        # Lazy import analyzers (they're optional)
        self._analyzers = {}
        self._init_analyzers()
    
    def _init_analyzers(self):
        """Initialize analyzer instances (lazy loading)."""
        # Core Web Vitals Analyzer
        if self.feature_flags.get('core_web_vitals'):
            try:
                from core_web_vitals_analyzer import CoreWebVitalsAnalyzer
                self._analyzers['core_web_vitals'] = CoreWebVitalsAnalyzer()
            except ImportError:
                self._analyzers['core_web_vitals'] = None
        
        # Advanced Performance Analyzer
        if self.feature_flags.get('advanced_performance'):
            try:
                from advanced_page_performance_analyzer import AdvancedPagePerformanceAnalyzer
                self._analyzers['advanced_performance'] = AdvancedPagePerformanceAnalyzer()
            except ImportError:
                self._analyzers['advanced_performance'] = None
        
        # Render & Loading Analyzer
        if self.feature_flags.get('render_loading'):
            try:
                from render_loading_analyzer import RenderLoadingAnalyzer
                self._analyzers['render_loading'] = RenderLoadingAnalyzer()
            except ImportError:
                self._analyzers['render_loading'] = None
        
        # Indexability Analyzer
        if self.feature_flags.get('indexability'):
            try:
                from indexability_crawlability_analyzer import IndexabilityCrawlabilityAnalyzer
                self._analyzers['indexability'] = IndexabilityCrawlabilityAnalyzer()
            except ImportError:
                self._analyzers['indexability'] = None
        
        # Security Analyzer
        if self.feature_flags.get('security'):
            try:
                from security_trust_analyzer import SecurityTrustAnalyzer
                self._analyzers['security'] = SecurityTrustAnalyzer()
            except ImportError:
                self._analyzers['security'] = None
        
        # Comprehensive Scorer
        if self.feature_flags.get('comprehensive_scoring'):
            try:
                from comprehensive_seo_scorer import ComprehensiveSEOScorer
                self._analyzers['scorer'] = ComprehensiveSEOScorer()
            except ImportError:
                self._analyzers['scorer'] = None
    
    def analyze_page(self, page_data: Dict, html_content: str, page_url: str, 
                     response_headers: Optional[Dict] = None) -> Dict:
        """
        Analyze a single page with all enabled analyzers.
        
        Args:
            page_data: Existing page data dictionary
            html_content: HTML content of the page
            page_url: URL of the page
            response_headers: Optional HTTP response headers
            
        Returns:
            Dictionary with all analysis results added to page_data
        """
        analysis_results = {}
        
        # Core Web Vitals (only if explicitly enabled via config, as it's expensive)
        if self.feature_flags.get('core_web_vitals') and self.feature_flags.get('use_playwright_for_cwv'):
            analyzer = self._analyzers.get('core_web_vitals')
            if analyzer:
                try:
                    # Use sync wrapper for compatibility
                    cwv_results = analyzer.analyze_page_sync(page_url, html_content)
                    analysis_results['core_web_vitals'] = cwv_results
                except Exception as e:
                    analysis_results['core_web_vitals'] = {'error': str(e)}
        
        # Advanced Performance Analysis
        if self.feature_flags.get('advanced_performance'):
            analyzer = self._analyzers.get('advanced_performance')
            if analyzer:
                try:
                    perf_results = analyzer.analyze_page(html_content, page_url)
                    analysis_results['advanced_performance'] = perf_results
                except Exception as e:
                    analysis_results['advanced_performance'] = {'error': str(e)}
        
        # Render & Loading Analysis
        if self.feature_flags.get('render_loading'):
            analyzer = self._analyzers.get('render_loading')
            if analyzer:
                try:
                    render_results = analyzer.analyze_page(html_content, page_url)
                    analysis_results['render_loading_analysis'] = render_results
                except Exception as e:
                    analysis_results['render_loading_analysis'] = {'error': str(e)}
        
        # Indexability & Crawlability Analysis
        if self.feature_flags.get('indexability'):
            analyzer = self._analyzers.get('indexability')
            if analyzer:
                try:
                    index_results = analyzer.analyze_page(html_content, page_url, response_headers)
                    analysis_results['indexability_analysis'] = index_results
                except Exception as e:
                    analysis_results['indexability_analysis'] = {'error': str(e)}
        
        # Security & Trust Analysis
        if self.feature_flags.get('security'):
            analyzer = self._analyzers.get('security')
            if analyzer:
                try:
                    security_results = analyzer.analyze_page(html_content, page_url, response_headers)
                    analysis_results['security_analysis'] = security_results
                except Exception as e:
                    analysis_results['security_analysis'] = {'error': str(e)}
        
        # Merge analysis results into page_data
        page_data.update(analysis_results)
        
        # Comprehensive Scoring (requires all analysis to be done)
        if self.feature_flags.get('comprehensive_scoring'):
            scorer = self._analyzers.get('scorer')
            if scorer:
                try:
                    page_score = scorer.calculate_page_score(page_data)
                    page_data['comprehensive_seo_score'] = page_score
                except Exception as e:
                    page_data['comprehensive_seo_score'] = {'error': str(e)}
        
        return page_data
    
    def analyze_site(self, pages: List[Dict]) -> Dict:
        """
        Analyze entire site and calculate site-wide scores.
        
        Args:
            pages: List of page data dictionaries (with analysis already done)
            
        Returns:
            Dictionary with site-wide analysis
        """
        site_analysis = {}
        
        # Site-wide scoring
        if self.feature_flags.get('comprehensive_scoring'):
            scorer = self._analyzers.get('scorer')
            if scorer:
                try:
                    site_score = scorer.calculate_site_score(pages)
                    site_analysis['comprehensive_site_score'] = site_score
                except Exception as e:
                    site_analysis['comprehensive_site_score'] = {'error': str(e)}
        
        return site_analysis
    
    def get_available_analyzers(self) -> List[str]:
        """Get list of available (non-None) analyzers."""
        return [name for name, analyzer in self._analyzers.items() if analyzer is not None]
    
    def get_analysis_config(self) -> Dict:
        """Get current analysis configuration."""
        return {
            'feature_flags': self.feature_flags.copy(),
            'available_analyzers': self.get_available_analyzers()
        }

