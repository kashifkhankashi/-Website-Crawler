"""
Export Utilities - PDF, CSV, Excel Export
Professional export functionality
"""
from typing import Dict, List
import csv
import json
import io
from datetime import datetime


class ExportUtils:
    """
    Export competitor analysis results to various formats
    """
    
    @staticmethod
    def export_to_csv(data: Dict, filename: str = None) -> str:
        """
        Export analysis results to CSV
        
        Args:
            data: Analysis results dictionary
            filename: Optional filename
            
        Returns:
            CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Metric', 'Your Site', 'Competitor', 'Winner', 'Difference'])
        
        # Overall scores
        your_site = data.get('your_site', {})
        competitor = data.get('competitor', {})
        comparison = data.get('comparison', {})
        
        writer.writerow(['Overall Score', 
                         your_site.get('overall_score', 0),
                         competitor.get('overall_score', 0),
                         data.get('winner', {}).get('overall', 'tie'),
                         round((your_site.get('overall_score', 0) - competitor.get('overall_score', 0)), 1)])
        
        # SEO Scores
        writer.writerow(['SEO Score',
                         your_site.get('seo_score', 0),
                         competitor.get('seo_score', 0),
                         comparison.get('seo', {}).get('seo_score', {}).get('winner', 'tie'),
                         comparison.get('seo', {}).get('seo_score', {}).get('difference', 0)])
        
        # Performance
        writer.writerow(['Load Time (s)',
                         your_site.get('load_time', 0),
                         competitor.get('load_time', 0),
                         comparison.get('performance', {}).get('load_time', {}).get('winner', 'tie'),
                         round(comparison.get('performance', {}).get('load_time', {}).get('difference', 0), 3)])
        
        # Word Count
        writer.writerow(['Word Count',
                         your_site.get('word_count', 0),
                         competitor.get('word_count', 0),
                         'N/A',
                         comparison.get('seo', {}).get('word_count', {}).get('difference', 0)])
        
        # Images
        writer.writerow(['Images Alt Coverage (%)',
                         your_site.get('images_alt_coverage', 0),
                         competitor.get('images_alt_coverage', 0),
                         'N/A',
                         round((your_site.get('images_alt_coverage', 0) - competitor.get('images_alt_coverage', 0)), 1)])
        
        return output.getvalue()
    
    @staticmethod
    def export_to_json(data: Dict, pretty: bool = True) -> str:
        """
        Export analysis results to JSON
        
        Args:
            data: Analysis results dictionary
            pretty: Whether to format JSON nicely
            
        Returns:
            JSON content as string
        """
        if pretty:
            return json.dumps(data, indent=2, default=str)
        else:
            return json.dumps(data, default=str)
    
    @staticmethod
    def generate_summary_report(data: Dict) -> str:
        """
        Generate human-readable summary report
        
        Args:
            data: Analysis results dictionary
            
        Returns:
            Summary report as string
        """
        your_site = data.get('your_site', {})
        competitor = data.get('competitor', {})
        winner = data.get('winner', {})
        insights = data.get('insights', [])
        recommendations = data.get('recommendations', [])
        
        report = []
        report.append("=" * 80)
        report.append("COMPETITOR ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall Winner
        report.append("OVERALL WINNER")
        report.append("-" * 80)
        overall_winner = winner.get('overall', 'tie')
        if overall_winner == 'your_site':
            report.append("🏆 Your Site Wins!")
        elif overall_winner == 'competitor':
            report.append("🏆 Competitor Wins")
        else:
            report.append("🤝 It's a Tie!")
        report.append(f"Summary: {winner.get('summary', 'N/A')}")
        report.append("")
        
        # Scores
        report.append("SCORE COMPARISON")
        report.append("-" * 80)
        report.append(f"Your Site Overall Score: {your_site.get('overall_score', 0)}/100")
        report.append(f"Competitor Overall Score: {competitor.get('overall_score', 0)}/100")
        report.append("")
        report.append(f"Your Site SEO Score: {your_site.get('seo_score', 0)}/100")
        report.append(f"Competitor SEO Score: {competitor.get('seo_score', 0)}/100")
        report.append("")
        report.append(f"Your Site Performance Score: {your_site.get('performance_score', 0)}/100")
        report.append(f"Competitor Performance Score: {competitor.get('performance_score', 0)}/100")
        report.append("")
        
        # Key Insights
        if insights:
            report.append("KEY INSIGHTS")
            report.append("-" * 80)
            for i, insight in enumerate(insights, 1):
                report.append(f"{i}. {insight}")
            report.append("")
        
        # Recommendations
        if recommendations:
            report.append("RECOMMENDATIONS")
            report.append("-" * 80)
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. [{rec.get('priority', 'medium').upper()}] {rec.get('category', 'General')}")
                report.append(f"   Action: {rec.get('action', 'N/A')}")
                report.append(f"   Reason: {rec.get('reason', 'N/A')}")
                report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)

