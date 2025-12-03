"""
Accessibility Analysis Module
WCAG compliance and accessibility checks
"""
from typing import Dict, List
from bs4 import BeautifulSoup
import re


class AccessibilityAnalyzer:
    """
    Accessibility analysis:
    - WCAG compliance
    - ARIA labels
    - Color contrast
    - Keyboard navigation
    - Screen reader support
    """
    
    def __init__(self):
        pass
    
    def analyze_accessibility(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Comprehensive accessibility analysis
        
        Args:
            soup: BeautifulSoup object
            url: Page URL
            
        Returns:
            Dictionary with accessibility analysis
        """
        # Basic checks
        images = soup.find_all('img')
        links = soup.find_all('a', href=True)
        forms = soup.find_all('form')
        inputs = soup.find_all(['input', 'textarea', 'select'])
        
        # Image alt text analysis
        image_analysis = self._analyze_images(images)
        
        # Link accessibility
        link_analysis = self._analyze_links(links)
        
        # Form accessibility
        form_analysis = self._analyze_forms(forms, inputs)
        
        # ARIA analysis
        aria_analysis = self._analyze_aria(soup)
        
        # Color contrast (basic check)
        contrast_analysis = self._analyze_contrast(soup)
        
        # Semantic HTML
        semantic_analysis = self._analyze_semantic_html(soup)
        
        # Calculate WCAG score
        wcag_score = self._calculate_wcag_score(
            image_analysis, link_analysis, form_analysis,
            aria_analysis, semantic_analysis
        )
        
        return {
            'wcag_score': wcag_score,
            'wcag_level': self._get_wcag_level(wcag_score),
            'image_analysis': image_analysis,
            'link_analysis': link_analysis,
            'form_analysis': form_analysis,
            'aria_analysis': aria_analysis,
            'contrast_analysis': contrast_analysis,
            'semantic_analysis': semantic_analysis,
            'issues': self._collect_issues(
                image_analysis, link_analysis, form_analysis,
                aria_analysis, semantic_analysis
            ),
            'recommendations': self._generate_recommendations(
                image_analysis, link_analysis, form_analysis,
                aria_analysis, semantic_analysis
            )
        }
    
    def _analyze_images(self, images: List) -> Dict:
        """Analyze image accessibility"""
        total = len(images)
        with_alt = 0
        without_alt = 0
        empty_alt = 0
        decorative = 0
        
        for img in images:
            alt = img.get('alt', '')
            if alt is None:
                without_alt += 1
            elif alt.strip() == '':
                empty_alt += 1
                # Check if marked as decorative
                role = img.get('role', '')
                if role == 'presentation' or 'decorative' in str(img.get('class', [])).lower():
                    decorative += 1
            else:
                with_alt += 1
        
        return {
            'total': total,
            'with_alt': with_alt,
            'without_alt': without_alt,
            'empty_alt': empty_alt,
            'decorative': decorative,
            'alt_coverage': round((with_alt / total * 100) if total > 0 else 0, 1),
            'score': round((with_alt / total * 100) if total > 0 else 0, 1)
        }
    
    def _analyze_links(self, links: List) -> Dict:
        """Analyze link accessibility"""
        total = len(links)
        with_text = 0
        without_text = 0
        generic_text = 0
        aria_labels = 0
        
        generic_anchors = ['click here', 'read more', 'here', 'link', 'more']
        
        for link in links:
            text = link.get_text(strip=True)
            aria_label = link.get('aria-label', '')
            
            if aria_label:
                aria_labels += 1
            
            if not text or text.strip() == '':
                without_text += 1
            elif text.lower().strip() in generic_anchors:
                generic_text += 1
            else:
                with_text += 1
        
        return {
            'total': total,
            'with_text': with_text,
            'without_text': without_text,
            'generic_text': generic_text,
            'with_aria_labels': aria_labels,
            'score': round(((with_text - generic_text) / total * 100) if total > 0 else 0, 1)
        }
    
    def _analyze_forms(self, forms: List, inputs: List) -> Dict:
        """Analyze form accessibility"""
        total_forms = len(forms)
        total_inputs = len(inputs)
        
        inputs_with_labels = 0
        inputs_without_labels = 0
        inputs_with_aria_labels = 0
        
        for input_elem in inputs:
            input_id = input_elem.get('id', '')
            aria_label = input_elem.get('aria-label', '')
            aria_labelledby = input_elem.get('aria-labelledby', '')
            
            # Check for associated label
            has_label = False
            if input_id:
                label = input_elem.find_parent().find('label', {'for': input_id})
                if label:
                    has_label = True
            
            if aria_label or aria_labelledby:
                inputs_with_aria_labels += 1
                has_label = True
            
            if has_label:
                inputs_with_labels += 1
            else:
                inputs_without_labels += 1
        
        return {
            'total_forms': total_forms,
            'total_inputs': total_inputs,
            'inputs_with_labels': inputs_with_labels,
            'inputs_without_labels': inputs_without_labels,
            'inputs_with_aria': inputs_with_aria_labels,
            'label_coverage': round((inputs_with_labels / total_inputs * 100) if total_inputs > 0 else 0, 1),
            'score': round((inputs_with_labels / total_inputs * 100) if total_inputs > 0 else 0, 1)
        }
    
    def _analyze_aria(self, soup: BeautifulSoup) -> Dict:
        """Analyze ARIA usage"""
        # Find elements with ARIA attributes
        aria_elements = soup.find_all(attrs=lambda x: x and any(
            attr.startswith('aria-') for attr in x.keys()
        ))
        
        aria_roles = soup.find_all(attrs={'role': True})
        aria_labels = soup.find_all(attrs={'aria-label': True})
        aria_labelledby = soup.find_all(attrs={'aria-labelledby': True})
        aria_describedby = soup.find_all(attrs={'aria-describedby': True})
        
        # Check for common ARIA patterns
        landmarks = soup.find_all(attrs={'role': re.compile(r'(banner|navigation|main|complementary|contentinfo|search)')})
        
        return {
            'total_aria_elements': len(aria_elements),
            'aria_roles': len(aria_roles),
            'aria_labels': len(aria_labels),
            'aria_labelledby': len(aria_labelledby),
            'aria_describedby': len(aria_describedby),
            'landmarks': len(landmarks),
            'score': min(100, len(aria_elements) * 2)  # Basic scoring
        }
    
    def _analyze_contrast(self, soup: BeautifulSoup) -> Dict:
        """Basic color contrast analysis"""
        # This is a simplified check - full contrast requires CSS analysis
        # Check for inline styles with color
        elements_with_color = soup.find_all(attrs={'style': re.compile(r'color:', re.I)})
        
        # Check for color attributes (deprecated but still used)
        elements_with_color_attr = soup.find_all(attrs={'color': True})
        
        return {
            'inline_styles_with_color': len(elements_with_color),
            'color_attributes': len(elements_with_color_attr),
            'note': 'Full contrast analysis requires CSS parsing',
            'score': 50  # Placeholder
        }
    
    def _analyze_semantic_html(self, soup: BeautifulSoup) -> Dict:
        """Analyze semantic HTML usage"""
        semantic_elements = {
            'header': len(soup.find_all('header')),
            'footer': len(soup.find_all('footer')),
            'main': len(soup.find_all('main')),
            'article': len(soup.find_all('article')),
            'section': len(soup.find_all('section')),
            'aside': len(soup.find_all('aside')),
            'nav': len(soup.find_all('nav')),
            'figure': len(soup.find_all('figure')),
            'figcaption': len(soup.find_all('figcaption')),
            'time': len(soup.find_all('time')),
            'mark': len(soup.find_all('mark'))
        }
        
        total_semantic = sum(semantic_elements.values())
        
        return {
            'elements': semantic_elements,
            'total_semantic_elements': total_semantic,
            'score': min(100, total_semantic * 10)
        }
    
    def _calculate_wcag_score(self, image_analysis: Dict, link_analysis: Dict,
                             form_analysis: Dict, aria_analysis: Dict,
                             semantic_analysis: Dict) -> float:
        """Calculate overall WCAG compliance score"""
        scores = []
        
        # Image alt text (25%)
        scores.append(('image', image_analysis.get('score', 0), 0.25))
        
        # Link accessibility (20%)
        scores.append(('link', link_analysis.get('score', 0), 0.20))
        
        # Form accessibility (20%)
        scores.append(('form', form_analysis.get('score', 0), 0.20))
        
        # ARIA usage (15%)
        scores.append(('aria', aria_analysis.get('score', 0), 0.15))
        
        # Semantic HTML (20%)
        scores.append(('semantic', semantic_analysis.get('score', 0), 0.20))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        return round(total_score, 1)
    
    def _get_wcag_level(self, score: float) -> str:
        """Get WCAG compliance level"""
        if score >= 90:
            return 'AAA (Excellent)'
        elif score >= 75:
            return 'AA (Good)'
        elif score >= 60:
            return 'A (Basic)'
        else:
            return 'Non-compliant'
    
    def _collect_issues(self, image_analysis: Dict, link_analysis: Dict,
                       form_analysis: Dict, aria_analysis: Dict,
                       semantic_analysis: Dict) -> List[str]:
        """Collect accessibility issues"""
        issues = []
        
        if image_analysis.get('without_alt', 0) > 0:
            issues.append(f"{image_analysis['without_alt']} images missing alt text")
        
        if link_analysis.get('without_text', 0) > 0:
            issues.append(f"{link_analysis['without_text']} links without descriptive text")
        
        if form_analysis.get('inputs_without_labels', 0) > 0:
            issues.append(f"{form_analysis['inputs_without_labels']} form inputs without labels")
        
        if semantic_analysis.get('total_semantic_elements', 0) == 0:
            issues.append("No semantic HTML5 elements found")
        
        return issues
    
    def _generate_recommendations(self, image_analysis: Dict, link_analysis: Dict,
                                 form_analysis: Dict, aria_analysis: Dict,
                                 semantic_analysis: Dict) -> List[str]:
        """Generate accessibility recommendations"""
        recommendations = []
        
        if image_analysis.get('alt_coverage', 100) < 100:
            recommendations.append(f"Add alt text to {image_analysis.get('without_alt', 0)} images")
        
        if link_analysis.get('generic_text', 0) > 0:
            recommendations.append(f"Replace {link_analysis.get('generic_text', 0)} generic link texts with descriptive text")
        
        if form_analysis.get('label_coverage', 100) < 100:
            recommendations.append(f"Add labels to {form_analysis.get('inputs_without_labels', 0)} form inputs")
        
        if aria_analysis.get('landmarks', 0) == 0:
            recommendations.append("Add ARIA landmarks for better navigation")
        
        if semantic_analysis.get('total_semantic_elements', 0) < 5:
            recommendations.append("Use more semantic HTML5 elements (header, nav, main, article, section)")
        
        return recommendations

