"""
Comprehensive SEO Scoring System.

Provides:
- Page-level SEO score
- Site-wide health score
- Category-based scoring (Performance, SEO, Content, Technical)
- Issue severity levels (Critical, Warning, Opportunity)
- Clear fix recommendations for every issue
"""
from typing import Dict, List, Optional
from collections import defaultdict


class ComprehensiveSEOScorer:
    """
    Comprehensive SEO scoring system with category-based analysis.
    """
    
    def __init__(self):
        """Initialize the scorer."""
        self.severity_weights = {
            'critical': 10,
            'warning': 5,
            'info': 2,
            'opportunity': 1
        }
    
    def calculate_page_score(self, page_data: Dict) -> Dict:
        """
        Calculate comprehensive SEO score for a single page.
        
        Args:
            page_data: Dictionary containing page analysis data
            
        Returns:
            Dictionary with page score and breakdown
        """
        scores = {
            'performance': self._score_performance(page_data),
            'seo': self._score_seo(page_data),
            'content': self._score_content(page_data),
            'technical': self._score_technical(page_data)
        }
        
        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score(scores)
        
        # Collect all issues
        issues = self._collect_page_issues(page_data, scores)
        
        return {
            'overall_score': overall_score,
            'category_scores': scores,
            'issues': issues,
            'issue_counts': self._count_issues_by_severity(issues),
            'recommendations': self._generate_recommendations(issues)
        }
    
    def calculate_site_score(self, pages: List[Dict]) -> Dict:
        """
        Calculate site-wide health score.
        
        Args:
            pages: List of page data dictionaries
            
        Returns:
            Dictionary with site-wide score and analysis
        """
        if not pages:
            return {
                'overall_score': 0,
                'category_scores': {},
                'total_pages': 0,
                'page_scores': []
            }
        
        # Calculate scores for all pages
        page_scores = []
        category_totals = defaultdict(float)
        
        for page in pages:
            page_score = self.calculate_page_score(page)
            page_scores.append({
                'url': page.get('url', ''),
                'score': page_score['overall_score'],
                'category_scores': page_score['category_scores']
            })
            
            # Aggregate category scores
            for category, score in page_score['category_scores'].items():
                category_totals[category] += score
        
        # Calculate average category scores
        num_pages = len(pages)
        category_scores = {
            category: round(total / num_pages, 1)
            for category, total in category_totals.items()
        }
        
        # Calculate overall site score
        overall_score = self._calculate_overall_score(category_scores)
        
        # Aggregate site-wide issues
        all_issues = []
        for page in pages:
            page_score = self.calculate_page_score(page)
            for issue in page_score.get('issues', []):
                issue_copy = issue.copy()
                issue_copy['page_url'] = page.get('url', '')
                all_issues.append(issue_copy)
        
        # Count issues by type
        issue_counts = self._count_issues_by_type_and_severity(all_issues)
        
        return {
            'overall_score': round(overall_score, 1),
            'category_scores': category_scores,
            'total_pages': num_pages,
            'page_scores': page_scores,
            'site_wide_issues': all_issues[:100],  # Limit to first 100 issues
            'issue_counts': issue_counts,
            'top_issues': self._get_top_issues(all_issues)
        }
    
    def _score_performance(self, page_data: Dict) -> float:
        """Score performance category (0-100)."""
        score = 100.0
        deductions = []
        
        # Check Core Web Vitals
        cwv = page_data.get('core_web_vitals', {})
        if cwv:
            lcp_score = cwv.get('lcp_score', '')
            if lcp_score == 'poor':
                score -= 15
                deductions.append('LCP is poor')
            elif lcp_score == 'needs-improvement':
                score -= 8
                deductions.append('LCP needs improvement')
            
            cls_score = cwv.get('cls_score', '')
            if cls_score == 'poor':
                score -= 15
                deductions.append('CLS is poor')
            elif cls_score == 'needs-improvement':
                score -= 8
                deductions.append('CLS needs improvement')
            
            inp_score = cwv.get('inp_score', '')
            if inp_score == 'poor':
                score -= 10
                deductions.append('INP is poor')
            elif inp_score == 'needs-improvement':
                score -= 5
                deductions.append('INP needs improvement')
        
        # Check render-blocking resources
        render_loading = page_data.get('render_loading_analysis', {})
        if render_loading:
            blocking = render_loading.get('render_blocking_resources', {})
            blocking_count = blocking.get('total_blocking_resources', 0)
            if blocking_count > 5:
                score -= 10
                deductions.append(f'{blocking_count} render-blocking resources')
            elif blocking_count > 2:
                score -= 5
                deductions.append(f'{blocking_count} render-blocking resources')
        
        # Check page size
        perf = page_data.get('advanced_performance', {})
        if perf:
            summary = perf.get('resource_summary', {})
            total_mb = summary.get('total_page_size_mb', 0)
            if total_mb > 5:
                score -= 10
                deductions.append(f'Page size is {total_mb:.1f}MB')
            elif total_mb > 3:
                score -= 5
                deductions.append(f'Page size is {total_mb:.1f}MB')
        
        return max(0, score)
    
    def _score_seo(self, page_data: Dict) -> float:
        """Score SEO category (0-100)."""
        score = 100.0
        deductions = []
        
        # Title
        title = page_data.get('title', '')
        if not title:
            score -= 15
            deductions.append('Missing title tag')
        else:
            title_len = len(title)
            if title_len < 30:
                score -= 5
                deductions.append('Title too short')
            elif title_len > 60:
                score -= 5
                deductions.append('Title too long')
        
        # Meta description
        meta_desc = page_data.get('meta_description', '')
        if not meta_desc:
            score -= 10
            deductions.append('Missing meta description')
        else:
            desc_len = len(meta_desc)
            if desc_len < 120:
                score -= 5
                deductions.append('Meta description too short')
            elif desc_len > 160:
                score -= 5
                deductions.append('Meta description too long')
        
        # H1 tags
        h1_tags = page_data.get('h1_tags', [])
        if len(h1_tags) == 0:
            score -= 10
            deductions.append('Missing H1 tag')
        elif len(h1_tags) > 1:
            score -= 5
            deductions.append('Multiple H1 tags')
        
        # Images without alt
        images = page_data.get('images', [])
        images_without_alt = [img for img in images if not img.get('alt', '').strip()]
        if images_without_alt:
            missing_alt_pct = (len(images_without_alt) / len(images)) * 100 if images else 0
            if missing_alt_pct > 50:
                score -= 10
                deductions.append(f'{missing_alt_pct:.0f}% of images missing alt text')
            elif missing_alt_pct > 25:
                score -= 5
                deductions.append(f'{missing_alt_pct:.0f}% of images missing alt text')
        
        # Canonical
        if not page_data.get('canonical_url'):
            score -= 5
            deductions.append('Missing canonical URL')
        
        # Indexability
        indexability = page_data.get('indexability_analysis', {})
        if indexability:
            status = indexability.get('indexability_status', 'indexable')
            if status != 'indexable':
                score -= 20
                deductions.append(f'Page not indexable: {status}')
        
        return max(0, score)
    
    def _score_content(self, page_data: Dict) -> float:
        """Score content category (0-100)."""
        score = 100.0
        deductions = []
        
        # Word count
        word_count = page_data.get('word_count', 0)
        if word_count < 300:
            score -= 20
            deductions.append('Thin content (less than 300 words)')
        elif word_count < 500:
            score -= 10
            deductions.append('Content could be longer')
        
        # Duplicate content
        if page_data.get('is_exact_duplicate'):
            score -= 30
            deductions.append('Exact duplicate content')
        else:
            similarity_scores = page_data.get('similarity_scores', {})
            if similarity_scores:
                max_similarity = max(similarity_scores.values()) if similarity_scores else 0
                if max_similarity >= 90:
                    score -= 25
                    deductions.append('High duplicate content')
                elif max_similarity >= 70:
                    score -= 15
                    deductions.append('Medium duplicate content')
        
        # Heading structure
        h1_count = len(page_data.get('h1_tags', []))
        h2_count = len(page_data.get('h2_tags', []))
        if h1_count == 0:
            score -= 10
            deductions.append('No H1 tag')
        if h2_count == 0 and word_count > 500:
            score -= 5
            deductions.append('No H2 tags for content structure')
        
        return max(0, score)
    
    def _score_technical(self, page_data: Dict) -> float:
        """Score technical category (0-100)."""
        score = 100.0
        deductions = []
        
        # HTTPS
        security = page_data.get('security_analysis', {})
        if security:
            https = security.get('https_enforcement', {})
            if not https.get('is_https'):
                score -= 20
                deductions.append('Not served over HTTPS')
            
            # Mixed content
            mixed_content = security.get('mixed_content', {})
            if mixed_content.get('has_mixed_content'):
                count = mixed_content.get('count', 0)
                score -= min(20, count * 2)
                deductions.append(f'{count} mixed content resources')
            
            # Security headers
            headers = security.get('security_headers', {})
            missing_count = headers.get('missing_count', 0)
            if missing_count > 3:
                score -= 10
                deductions.append(f'{missing_count} missing security headers')
        
        # Broken links
        broken_links = page_data.get('broken_links', [])
        if broken_links:
            broken_count = len(broken_links)
            score -= min(15, broken_count * 3)
            deductions.append(f'{broken_count} broken links')
        
        # Status code
        status_code = page_data.get('status_code', 200)
        if status_code >= 400:
            score -= 30
            deductions.append(f'HTTP {status_code} status')
        elif status_code >= 300:
            score -= 5
            deductions.append(f'Redirect ({status_code})')
        
        return max(0, score)
    
    def _calculate_overall_score(self, category_scores: Dict) -> float:
        """Calculate weighted overall score from category scores."""
        # Equal weighting for now (can be adjusted)
        weights = {
            'performance': 0.25,
            'seo': 0.30,
            'content': 0.25,
            'technical': 0.20
        }
        
        total_weighted = 0.0
        total_weight = 0.0
        
        for category, weight in weights.items():
            score = category_scores.get(category, 0)
            total_weighted += score * weight
            total_weight += weight
        
        return total_weighted / total_weight if total_weight > 0 else 0.0
    
    def _collect_page_issues(self, page_data: Dict, scores: Dict) -> List[Dict]:
        """Collect all issues for a page."""
        issues = []
        
        # Performance issues
        if scores['performance'] < 70:
            issues.append({
                'category': 'performance',
                'severity': 'warning' if scores['performance'] < 50 else 'info',
                'issue': f'Performance score is {scores["performance"]:.1f}/100',
                'recommendation': 'Improve Core Web Vitals and reduce render-blocking resources'
            })
        
        # SEO issues
        if scores['seo'] < 70:
            issues.append({
                'category': 'seo',
                'severity': 'warning' if scores['seo'] < 50 else 'info',
                'issue': f'SEO score is {scores["seo"]:.1f}/100',
                'recommendation': 'Fix on-page SEO elements (title, meta, headings, images)'
            })
        
        # Content issues
        if scores['content'] < 70:
            issues.append({
                'category': 'content',
                'severity': 'warning' if scores['content'] < 50 else 'info',
                'issue': f'Content score is {scores["content"]:.1f}/100',
                'recommendation': 'Improve content quality and reduce duplication'
            })
        
        # Technical issues
        if scores['technical'] < 70:
            issues.append({
                'category': 'technical',
                'severity': 'warning' if scores['technical'] < 50 else 'info',
                'issue': f'Technical score is {scores["technical"]:.1f}/100',
                'recommendation': 'Fix technical issues (HTTPS, security headers, broken links)'
            })
        
        return issues
    
    def _count_issues_by_severity(self, issues: List[Dict]) -> Dict:
        """Count issues by severity level."""
        counts = defaultdict(int)
        for issue in issues:
            severity = issue.get('severity', 'info')
            counts[severity] += 1
        return dict(counts)
    
    def _count_issues_by_type_and_severity(self, issues: List[Dict]) -> Dict:
        """Count issues by type and severity."""
        counts = defaultdict(lambda: defaultdict(int))
        for issue in issues:
            category = issue.get('category', 'other')
            severity = issue.get('severity', 'info')
            counts[category][severity] += 1
        return {k: dict(v) for k, v in counts.items()}
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate actionable recommendations from issues."""
        recommendations = []
        
        # Group by category and severity
        by_category = defaultdict(list)
        for issue in issues:
            category = issue.get('category', 'other')
            by_category[category].append(issue)
        
        # Generate top recommendations per category
        for category, cat_issues in by_category.items():
            critical = [i for i in cat_issues if i.get('severity') == 'critical']
            if critical:
                recommendations.append(f"Fix {len(critical)} critical {category} issues")
            else:
                warnings = [i for i in cat_issues if i.get('severity') == 'warning']
                if warnings:
                    recommendations.append(f"Address {len(warnings)} {category} warnings")
        
        return recommendations[:10]  # Limit to top 10
    
    def _get_top_issues(self, issues: List[Dict], limit: int = 20) -> List[Dict]:
        """Get top issues by severity."""
        severity_order = {'critical': 0, 'warning': 1, 'info': 2, 'opportunity': 3}
        sorted_issues = sorted(
            issues,
            key=lambda x: (severity_order.get(x.get('severity', 'info'), 99), x.get('category', ''))
        )
        return sorted_issues[:limit]

