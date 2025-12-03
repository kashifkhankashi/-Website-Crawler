"""
Content Intelligence & Gap Analysis
Professional implementation for content analysis
"""
from typing import Dict, List, Set, Tuple
from bs4 import BeautifulSoup
import re
from collections import Counter
import math


class ContentAnalyzer:
    """
    Advanced content analysis:
    - Topic modeling
    - Content gap detection
    - Sentiment analysis
    - Content freshness
    - Readability analysis
    """
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
    
    def analyze_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Comprehensive content analysis
        
        Args:
            soup: BeautifulSoup object
            url: Page URL
            
        Returns:
            Dictionary with content analysis results
        """
        # Extract text content
        text_content = self._extract_text(soup)
        
        # Basic metrics
        word_count = len(text_content.split())
        char_count = len(text_content)
        sentence_count = len(re.split(r'[.!?]+', text_content))
        
        # Extract topics
        topics = self._extract_topics(text_content)
        
        # Content structure
        structure = self._analyze_structure(soup)
        
        # Readability
        readability = self._calculate_readability(text_content, word_count, sentence_count)
        
        # Content quality
        quality = self._assess_quality(text_content, word_count, structure)
        
        # Content freshness indicators
        freshness = self._detect_freshness(soup, text_content)
        
        return {
            'text_content': text_content[:5000],  # First 5000 chars
            'word_count': word_count,
            'character_count': char_count,
            'sentence_count': sentence_count,
            'paragraph_count': structure.get('paragraph_count', 0),
            'topics': topics,
            'structure': structure,
            'readability': readability,
            'quality': quality,
            'freshness': freshness
        }
    
    def detect_content_gaps(self, your_content: Dict, competitor_content: Dict) -> Dict:
        """
        Detect content gaps between your site and competitor
        
        Args:
            your_content: Your site's content analysis
            competitor_content: Competitor's content analysis
            
        Returns:
            Dictionary with gap analysis
        """
        your_topics = set([topic['term'] for topic in your_content.get('topics', {}).get('main_topics', [])])
        competitor_topics = set([topic['term'] for topic in competitor_content.get('topics', {}).get('main_topics', [])])
        
        # Topics competitor covers that you don't
        missing_topics = competitor_topics - your_topics
        
        # Topics you cover that competitor doesn't
        unique_topics = your_topics - competitor_topics
        
        # Common topics
        common_topics = your_topics & competitor_topics
        
        # Content depth comparison
        your_word_count = your_content.get('word_count', 0)
        competitor_word_count = competitor_content.get('word_count', 0)
        word_count_diff = competitor_word_count - your_word_count
        
        # Readability comparison
        your_readability = your_content.get('readability', {}).get('score', 0)
        competitor_readability = competitor_content.get('readability', {}).get('score', 0)
        
        return {
            'missing_topics': list(missing_topics)[:20],  # Top 20
            'unique_topics': list(unique_topics)[:20],
            'common_topics': list(common_topics)[:20],
            'topic_coverage': {
                'your_coverage': len(your_topics),
                'competitor_coverage': len(competitor_topics),
                'overlap': len(common_topics),
                'gap_size': len(missing_topics)
            },
            'content_depth': {
                'your_words': your_word_count,
                'competitor_words': competitor_word_count,
                'difference': word_count_diff,
                'recommendation': self._get_depth_recommendation(word_count_diff)
            },
            'readability_comparison': {
                'your_score': your_readability,
                'competitor_score': competitor_readability,
                'difference': competitor_readability - your_readability
            },
            'recommendations': self._generate_content_recommendations(
                missing_topics, word_count_diff, your_readability, competitor_readability
            )
        }
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove scripts and styles
        for script in soup(["script", "style", "noscript", "meta", "link"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_topics(self, text: str) -> Dict:
        """Extract main topics using TF-IDF approximation"""
        if not text:
            return {'main_topics': [], 'topic_count': 0}
        
        # Tokenize
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        if not words:
            return {'main_topics': [], 'topic_count': 0}
        
        # Remove stop words
        filtered_words = [w for w in words if w not in self.stop_words]
        
        # Count frequencies
        word_freq = Counter(filtered_words)
        total_words = len(filtered_words)
        
        # Calculate importance (TF * IDF approximation)
        topics = []
        for word, count in word_freq.most_common(50):
            if count > 1:  # At least 2 occurrences
                tf = count / total_words
                idf = math.log(total_words / count) if count > 0 else 0
                importance = tf * idf * count
                
                topics.append({
                    'term': word,
                    'count': count,
                    'importance': round(importance, 4)
                })
        
        # Sort by importance
        topics.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'main_topics': topics[:30],  # Top 30
            'topic_count': len(topics),
            'unique_topics': len(set(filtered_words))
        }
    
    def _analyze_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze content structure"""
        paragraphs = soup.find_all('p')
        lists = soup.find_all(['ul', 'ol'])
        tables = soup.find_all('table')
        images = soup.find_all('img')
        videos = soup.find_all(['video', 'iframe'])
        
        # Heading structure
        headings = {
            'h1': len(soup.find_all('h1')),
            'h2': len(soup.find_all('h2')),
            'h3': len(soup.find_all('h3')),
            'h4': len(soup.find_all('h4')),
            'h5': len(soup.find_all('h5')),
            'h6': len(soup.find_all('h6'))
        }
        
        # Calculate structure score
        structure_score = 0
        if headings['h1'] == 1:
            structure_score += 20
        if headings['h2'] >= 2:
            structure_score += 20
        if len(paragraphs) >= 5:
            structure_score += 20
        if len(lists) > 0:
            structure_score += 10
        if len(images) > 0:
            structure_score += 10
        if len(tables) > 0:
            structure_score += 10
        if len(videos) > 0:
            structure_score += 10
        
        return {
            'paragraph_count': len(paragraphs),
            'list_count': len(lists),
            'table_count': len(tables),
            'image_count': len(images),
            'video_count': len(videos),
            'headings': headings,
            'structure_score': min(100, structure_score)
        }
    
    def _calculate_readability(self, text: str, word_count: int, sentence_count: int) -> Dict:
        """Calculate readability metrics"""
        if not text or word_count == 0 or sentence_count == 0:
            return {
                'score': 0,
                'grade': 'N/A',
                'level': 'N/A'
            }
        
        # Average sentence length
        avg_sentence_length = word_count / sentence_count
        
        # Count syllables (approximation)
        vowels = 'aeiouy'
        syllables = sum(1 for char in text.lower() if char in vowels)
        if syllables == 0:
            syllables = word_count
        
        avg_syllables = syllables / word_count if word_count > 0 else 0
        
        # Flesch Reading Ease
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        flesch_score = max(0, min(100, flesch_score))
        
        # Grade level
        if flesch_score >= 90:
            grade = '5th grade'
            level = 'Very Easy'
        elif flesch_score >= 80:
            grade = '6th grade'
            level = 'Easy'
        elif flesch_score >= 70:
            grade = '7th grade'
            level = 'Fairly Easy'
        elif flesch_score >= 60:
            grade = '8th-9th grade'
            level = 'Standard'
        elif flesch_score >= 50:
            grade = '10th-12th grade'
            level = 'Fairly Difficult'
        elif flesch_score >= 30:
            grade = 'College'
            level = 'Difficult'
        else:
            grade = 'College Graduate'
            level = 'Very Difficult'
        
        return {
            'score': round(flesch_score, 1),
            'grade': grade,
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_syllables_per_word': round(avg_syllables, 2)
        }
    
    def _assess_quality(self, text: str, word_count: int, structure: Dict) -> Dict:
        """Assess content quality"""
        quality_score = 0
        issues = []
        strengths = []
        
        # Word count
        if word_count >= 1000:
            quality_score += 30
            strengths.append('Comprehensive content (1000+ words)')
        elif word_count >= 500:
            quality_score += 20
            strengths.append('Good content depth (500+ words)')
        elif word_count >= 300:
            quality_score += 10
        else:
            issues.append('Thin content (less than 300 words)')
        
        # Structure
        if structure.get('structure_score', 0) >= 80:
            quality_score += 25
            strengths.append('Well-structured content')
        elif structure.get('structure_score', 0) >= 60:
            quality_score += 15
        
        # Paragraph count
        if structure.get('paragraph_count', 0) >= 5:
            quality_score += 15
            strengths.append('Good paragraph structure')
        elif structure.get('paragraph_count', 0) < 3:
            issues.append('Too few paragraphs')
        
        # Media
        if structure.get('image_count', 0) > 0:
            quality_score += 10
            strengths.append('Includes images')
        if structure.get('video_count', 0) > 0:
            quality_score += 10
            strengths.append('Includes videos')
        
        return {
            'score': min(100, quality_score),
            'issues': issues,
            'strengths': strengths,
            'overall': 'excellent' if quality_score >= 80 else 'good' if quality_score >= 60 else 'needs_improvement'
        }
    
    def _detect_freshness(self, soup: BeautifulSoup, text: str) -> Dict:
        """Detect content freshness indicators"""
        # Look for dates in text
        date_patterns = [
            r'\b(20\d{2})\b',  # Years like 2024
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+20\d{2}',
            r'\b(updated|last updated|published|last modified)',
            r'\b(202[0-9]|202[0-9])'
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text.lower())
            dates_found.extend(matches)
        
        # Check for "updated" or "last modified" text
        has_update_indicator = any(
            keyword in text.lower() 
            for keyword in ['updated', 'last updated', 'revised', 'modified', 'published']
        )
        
        return {
            'has_dates': len(dates_found) > 0,
            'date_count': len(dates_found),
            'has_update_indicator': has_update_indicator,
            'freshness_score': 50 if has_update_indicator else 30 if dates_found else 10
        }
    
    def _get_depth_recommendation(self, word_diff: int) -> str:
        """Get recommendation based on word count difference"""
        if word_diff > 500:
            return f"Consider expanding content by {word_diff} words to match competitor depth"
        elif word_diff > 200:
            return f"Add {word_diff} more words to improve content depth"
        elif word_diff < -200:
            return "Your content is more comprehensive than competitor"
        else:
            return "Content depth is comparable"
    
    def _generate_content_recommendations(self, missing_topics: Set, word_diff: int, 
                                         your_readability: float, competitor_readability: float) -> List[str]:
        """Generate actionable content recommendations"""
        recommendations = []
        
        if missing_topics:
            recommendations.append(f"Cover {len(missing_topics)} topics that competitor addresses: {', '.join(list(missing_topics)[:5])}")
        
        if word_diff > 300:
            recommendations.append(f"Expand content by approximately {word_diff} words for better depth")
        
        if competitor_readability > your_readability + 10:
            recommendations.append("Improve readability to match competitor's easier-to-read content")
        
        if not recommendations:
            recommendations.append("Content is competitive - maintain quality and freshness")
        
        return recommendations
    
    def _load_stop_words(self) -> Set[str]:
        """Load stop words list"""
        return {
            'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'their',
            'there', 'what', 'which', 'about', 'would', 'could', 'should', 'these',
            'those', 'them', 'they', 'were', 'where', 'when', 'than', 'then', 'more',
            'most', 'some', 'such', 'only', 'just', 'also', 'very', 'much', 'many',
            'into', 'over', 'after', 'under', 'through', 'during', 'before', 'above',
            'below', 'between', 'among', 'within', 'without', 'against', 'toward',
            'towards', 'around', 'throughout', 'beside', 'besides', 'except', 'beyond',
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'as', 'while',
            'until', 'for', 'to', 'of', 'in', 'on', 'at', 'by', 'up', 'about', 'into',
            'through', 'during', 'including', 'excluding', 'following', 'across',
            'behind', 'beyond', 'plus', 'except', 'but', 'per', 'via', 'am', 'is',
            'are', 'was', 'were', 'being', 'been', 'has', 'had', 'having', 'do',
            'does', 'did', 'done', 'can', 'cannot', 'could', 'may', 'might', 'must',
            'shall', 'should', 'ought', 'will', 'would', 'need', 'dare', 'used'
        }

