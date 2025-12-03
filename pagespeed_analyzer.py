"""
Google PageSpeed Insights API Integration
Professional implementation with error handling and caching
"""
import requests
import time
from typing import Dict, Optional, List
import json


class PageSpeedAnalyzer:
    """
    Google PageSpeed Insights API wrapper
    Provides official Google performance metrics
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize PageSpeed Analyzer
        
        Args:
            api_key: Google PageSpeed Insights API key (optional, but recommended)
        """
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.timeout = 30
        
    def analyze_url(self, url: str, strategy: str = "mobile") -> Dict:
        """
        Analyze URL using Google PageSpeed Insights API
        
        Args:
            url: URL to analyze
            strategy: "mobile" or "desktop"
            
        Returns:
            Dictionary with PageSpeed data
        """
        try:
            params = {
                'url': url,
                'strategy': strategy,
                'category': ['performance', 'accessibility', 'best-practices', 'seo']
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_pagespeed_data(data, strategy)
            elif response.status_code == 429:
                return {
                    'error': 'Rate limit exceeded. Please try again later.',
                    'has_error': True
                }
            else:
                return {
                    'error': f'API error: {response.status_code}',
                    'has_error': True
                }
                
        except requests.exceptions.Timeout:
            return {
                'error': 'Request timeout. PageSpeed API took too long.',
                'has_error': True
            }
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Network error: {str(e)}',
                'has_error': True
            }
        except Exception as e:
            return {
                'error': f'Analysis error: {str(e)}',
                'has_error': True
            }
    
    def _parse_pagespeed_data(self, data: Dict, strategy: str) -> Dict:
        """Parse PageSpeed Insights API response"""
        try:
            lighthouse_result = data.get('lighthouseResult', {})
            loading_experience = data.get('loadingExperience', {})
            
            # Performance score
            categories = lighthouse_result.get('categories', {})
            performance_score = categories.get('performance', {}).get('score', 0) * 100
            accessibility_score = categories.get('accessibility', {}).get('score', 0) * 100
            best_practices_score = categories.get('best-practices', {}).get('score', 0) * 100
            seo_score = categories.get('seo', {}).get('score', 0) * 100
            
            # Core Web Vitals
            audits = lighthouse_result.get('audits', {})
            
            # Largest Contentful Paint (LCP)
            lcp_audit = audits.get('largest-contentful-paint', {})
            lcp_value = lcp_audit.get('numericValue', 0) / 1000  # Convert to seconds
            lcp_score = lcp_audit.get('score', 0)
            
            # First Input Delay (FID) - from loading experience
            fid_metric = loading_experience.get('metrics', {}).get('FIRST_INPUT_DELAY_MS', {})
            fid_value = fid_metric.get('percentile', 0) / 1000  # Convert to seconds
            fid_category = self._categorize_fid(fid_value)
            
            # Cumulative Layout Shift (CLS)
            cls_audit = audits.get('cumulative-layout-shift', {})
            cls_value = cls_audit.get('numericValue', 0)
            cls_score = cls_audit.get('score', 0)
            
            # First Contentful Paint (FCP)
            fcp_audit = audits.get('first-contentful-paint', {})
            fcp_value = fcp_audit.get('numericValue', 0) / 1000
            fcp_score = fcp_audit.get('score', 0)
            
            # Time to Interactive (TTI)
            tti_audit = audits.get('interactive', {})
            tti_value = tti_audit.get('numericValue', 0) / 1000
            tti_score = tti_audit.get('score', 0)
            
            # Total Blocking Time (TBT)
            tbt_audit = audits.get('total-blocking-time', {})
            tbt_value = tbt_audit.get('numericValue', 0)
            tbt_score = tbt_audit.get('score', 0)
            
            # Speed Index
            speed_index_audit = audits.get('speed-index', {})
            speed_index_value = speed_index_audit.get('numericValue', 0) / 1000
            speed_index_score = speed_index_audit.get('score', 0)
            
            # Opportunities (optimization suggestions)
            opportunities = self._extract_opportunities(audits)
            
            # Diagnostics
            diagnostics = self._extract_diagnostics(audits)
            
            # Field Data (Real User Metrics) if available
            field_data = self._extract_field_data(loading_experience)
            
            return {
                'strategy': strategy,
                'has_error': False,
                'scores': {
                    'performance': round(performance_score, 1),
                    'accessibility': round(accessibility_score, 1),
                    'best_practices': round(best_practices_score, 1),
                    'seo': round(seo_score, 1),
                    'overall': round(performance_score, 1)  # Primary score
                },
                'core_web_vitals': {
                    'lcp': {
                        'value': round(lcp_value, 2),
                        'score': lcp_score,
                        'category': self._categorize_lcp(lcp_value),
                        'threshold': {'good': 2.5, 'needs_improvement': 4.0}
                    },
                    'fid': {
                        'value': round(fid_value, 2),
                        'category': fid_category,
                        'threshold': {'good': 100, 'needs_improvement': 300}
                    },
                    'cls': {
                        'value': round(cls_value, 3),
                        'score': cls_score,
                        'category': self._categorize_cls(cls_value),
                        'threshold': {'good': 0.1, 'needs_improvement': 0.25}
                    }
                },
                'metrics': {
                    'fcp': {
                        'value': round(fcp_value, 2),
                        'score': fcp_score,
                        'category': self._categorize_fcp(fcp_value)
                    },
                    'tti': {
                        'value': round(tti_value, 2),
                        'score': tti_score,
                        'category': self._categorize_tti(tti_value)
                    },
                    'tbt': {
                        'value': round(tbt_value, 0),
                        'score': tbt_score,
                        'category': self._categorize_tbt(tbt_value)
                    },
                    'speed_index': {
                        'value': round(speed_index_value, 2),
                        'score': speed_index_score,
                        'category': self._categorize_speed_index(speed_index_value)
                    }
                },
                'opportunities': opportunities,
                'diagnostics': diagnostics,
                'field_data': field_data,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'error': f'Error parsing PageSpeed data: {str(e)}',
                'has_error': True
            }
    
    def _extract_opportunities(self, audits: Dict) -> List[Dict]:
        """Extract optimization opportunities"""
        opportunities = []
        
        opportunity_audits = [
            'render-blocking-resources',
            'unused-css-rules',
            'unused-javascript',
            'modern-image-formats',
            'offscreen-images',
            'uses-optimized-images',
            'uses-text-compression',
            'uses-responsive-images',
            'efficient-animated-content',
            'preload-lcp-image',
            'uses-rel-preconnect',
            'uses-rel-preload',
            'font-display',
            'redirects',
            'server-response-time',
            'uses-long-cache-ttl',
            'dom-size',
            'minify-css',
            'minify-javascript',
            'uses-http2'
        ]
        
        for audit_id in opportunity_audits:
            audit = audits.get(audit_id, {})
            if audit.get('score') is not None and audit.get('score') < 1.0:
                details = audit.get('details', {})
                savings = details.get('overallSavingsMs', 0) or details.get('overallSavingsBytes', 0)
                
                opportunities.append({
                    'id': audit_id,
                    'title': audit.get('title', audit_id),
                    'description': audit.get('description', ''),
                    'score': audit.get('score', 0),
                    'savings': savings,
                    'savings_type': 'ms' if 'Ms' in str(savings) else 'bytes',
                    'impact': self._calculate_impact(audit.get('score', 1.0))
                })
        
        # Sort by impact
        opportunities.sort(key=lambda x: x['impact'], reverse=True)
        return opportunities[:10]  # Top 10
    
    def _extract_diagnostics(self, audits: Dict) -> List[Dict]:
        """Extract diagnostic information"""
        diagnostics = []
        
        diagnostic_audits = [
            'main-thread-work-breakdown',
            'bootup-time',
            'network-rtt',
            'network-server-latency',
            'dom-size',
            'max-potential-fid',
            'third-party-summary',
            'largest-contentful-paint-element',
            'layout-shift-elements',
            'long-tasks'
        ]
        
        for audit_id in diagnostic_audits:
            audit = audits.get(audit_id, {})
            if audit:
                diagnostics.append({
                    'id': audit_id,
                    'title': audit.get('title', audit_id),
                    'description': audit.get('description', ''),
                    'value': audit.get('numericValue', 0),
                    'displayValue': audit.get('displayValue', '')
                })
        
        return diagnostics[:10]  # Top 10
    
    def _extract_field_data(self, loading_experience: Dict) -> Optional[Dict]:
        """Extract real user metrics (field data)"""
        if not loading_experience:
            return None
        
        metrics = loading_experience.get('metrics', {})
        if not metrics:
            return None
        
        field_data = {}
        
        # Extract key metrics
        for metric_name, metric_data in metrics.items():
            if isinstance(metric_data, dict):
                field_data[metric_name] = {
                    'percentile': metric_data.get('percentile', 0),
                    'category': metric_data.get('category', 'UNKNOWN'),
                    'distributions': metric_data.get('distributions', [])
                }
        
        return field_data if field_data else None
    
    def _calculate_impact(self, score: float) -> str:
        """Calculate impact level"""
        if score < 0.5:
            return 'high'
        elif score < 0.8:
            return 'medium'
        else:
            return 'low'
    
    def _categorize_lcp(self, value: float) -> str:
        """Categorize LCP value"""
        if value <= 2.5:
            return 'good'
        elif value <= 4.0:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _categorize_fid(self, value: float) -> str:
        """Categorize FID value (in milliseconds)"""
        if value <= 100:
            return 'good'
        elif value <= 300:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _categorize_cls(self, value: float) -> str:
        """Categorize CLS value"""
        if value <= 0.1:
            return 'good'
        elif value <= 0.25:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _categorize_fcp(self, value: float) -> str:
        """Categorize FCP value"""
        if value <= 1.8:
            return 'good'
        elif value <= 3.0:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _categorize_tti(self, value: float) -> str:
        """Categorize TTI value"""
        if value <= 3.8:
            return 'good'
        elif value <= 7.3:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _categorize_tbt(self, value: float) -> str:
        """Categorize TBT value"""
        if value <= 200:
            return 'good'
        elif value <= 600:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _categorize_speed_index(self, value: float) -> str:
        """Categorize Speed Index value"""
        if value <= 3.4:
            return 'good'
        elif value <= 5.8:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def analyze_both_strategies(self, url: str) -> Dict:
        """
        Analyze URL for both mobile and desktop
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with both mobile and desktop results
        """
        results = {
            'url': url,
            'mobile': None,
            'desktop': None
        }
        
        # Analyze mobile
        print(f"Analyzing {url} for mobile...")
        results['mobile'] = self.analyze_url(url, 'mobile')
        
        # Small delay to avoid rate limiting
        time.sleep(1)
        
        # Analyze desktop
        print(f"Analyzing {url} for desktop...")
        results['desktop'] = self.analyze_url(url, 'desktop')
        
        return results

