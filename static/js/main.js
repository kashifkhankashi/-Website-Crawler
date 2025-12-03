// Main JavaScript for the crawler interface

let socket;
let currentJobId = null;

// Show crawl history
async function showHistory() {
    const historyCard = document.getElementById('historyCard');
    const historyContainer = document.getElementById('historyContainer');
    
    if (!historyCard || !historyContainer) return;
    
    historyCard.style.display = 'block';
    historyContainer.innerHTML = '<p class="loading">Loading crawl history...</p>';
    
    try {
        const response = await fetch('/api/list-jobs');
        const data = await response.json();
        
        if (!data.jobs || data.jobs.length === 0) {
            historyContainer.innerHTML = '<p style="text-align: center; color: var(--text-muted);">No crawl history found. Start your first crawl!</p>';
            return;
        }
        
        let html = '<div class="history-list">';
        data.jobs.forEach(job => {
            const date = new Date(job.started_at || job.completed_at || Date.now());
            const dateStr = date.toLocaleString();
            const statusBadge = job.status === 'completed' 
                ? '<span class="badge badge-success">Completed</span>'
                : job.status === 'crawling'
                ? '<span class="badge badge-info">Crawling</span>'
                : '<span class="badge badge-warning">' + job.status + '</span>';
            
            html += `
                <div class="history-item" onclick="viewHistoryJob('${job.job_id}')">
                    <div class="history-item-header">
                        <div class="history-item-title">
                            <strong>${job.url || 'Unknown URL'}</strong>
                            ${statusBadge}
                        </div>
                        <div class="history-item-meta">
                            <span><i class="fas fa-calendar"></i> ${dateStr}</span>
                        </div>
                    </div>
                    <div class="history-item-stats">
                        <span><i class="fas fa-file-alt"></i> ${job.pages_crawled || 0} pages</span>
                        <span><i class="fas fa-link"></i> ${job.links_found || 0} links</span>
                        ${job.site_seo_score !== null ? `<span><i class="fas fa-star"></i> SEO: ${job.site_seo_score}/100</span>` : ''}
                    </div>
                </div>
            `;
        });
        html += '</div>';
        historyContainer.innerHTML = html;
    } catch (error) {
        console.error('Error loading history:', error);
        historyContainer.innerHTML = '<p class="error">Error loading crawl history. Please try again.</p>';
    }
}

// Hide crawl history
function hideHistory() {
    const historyCard = document.getElementById('historyCard');
    if (historyCard) {
        historyCard.style.display = 'none';
    }
}

// View a historical job
function viewHistoryJob(jobId) {
    window.location.href = `/results/${jobId}`;
}

// Show competitor analyzer
function showCompetitorAnalyzer() {
    const competitorCard = document.getElementById('competitorCard');
    const mainContent = document.getElementById('mainContent');
    const loginCard = document.getElementById('loginCard');
    
    // Hide other sections
    if (mainContent) {
        mainContent.style.display = 'none';
    }
    if (loginCard) {
        loginCard.style.display = 'none';
    }
    
    // Show competitor analyzer
    if (competitorCard) {
        competitorCard.style.display = 'block';
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        console.error('competitorCard element not found!');
        alert('Competitor Analyzer section not found. Please refresh the page.');
    }
}

// Hide competitor analyzer
function hideCompetitorAnalyzer() {
    const competitorCard = document.getElementById('competitorCard');
    const mainContent = document.getElementById('mainContent');
    
    // Hide competitor analyzer
    if (competitorCard) {
        competitorCard.style.display = 'none';
    }
    
    // Show main content
    if (mainContent) {
        mainContent.style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Analyze competitors
async function analyzeCompetitors(event) {
    event.preventDefault();
    
    const yourUrl = document.getElementById('yourUrl').value.trim();
    const competitorUrl = document.getElementById('competitorUrl').value.trim();
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsDiv = document.getElementById('competitorResults');
    
    if (!yourUrl || !competitorUrl) {
        alert('Please enter both URLs');
        return;
    }
    
    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    resultsDiv.style.display = 'none';
    
    try {
        const response = await fetch('/api/analyze-competitors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url1: yourUrl,
                url2: competitorUrl
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }
        
        const data = await response.json();
        displayCompetitorResults(data);
        resultsDiv.style.display = 'block';
        
    } catch (error) {
        console.error('Error analyzing competitors:', error);
        alert('Error: ' + error.message);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Competitors';
    }
}

// Display competitor analysis results
function displayCompetitorResults(data) {
    const resultsDiv = document.getElementById('competitorResults');
    if (!resultsDiv) return;
    
    const yourSite = data.your_site || {};
    const competitor = data.competitor || {};
    const comparison = data.comparison || {};
    const winner = data.winner || {};
    const insights = data.insights || [];
    const recommendations = data.recommendations || [];
    const advantage = data.advantage_score || {};
    
    let html = `
        <div class="competitor-results">
            <div class="competitor-header">
                <h3><i class="fas fa-trophy"></i> Overall Winner: ${winner.overall === 'your_site' ? 'Your Site 🏆' : winner.overall === 'competitor' ? 'Competitor 🏆' : 'Tie 🤝'}</h3>
                <p class="winner-summary">${winner.summary || ''}</p>
                ${advantage.advantage_percentage !== undefined ? `
                    <div class="advantage-score">
                        <div class="advantage-circle">
                            <span class="advantage-value">${advantage.advantage_percentage}%</span>
                            <span class="advantage-label">${advantage.advantage_level || 'Competitive'}</span>
                        </div>
                        <p>Your Competitive Advantage Score</p>
                    </div>
                ` : ''}
            </div>
            
            ${advantage.winning_categories && advantage.winning_categories.length > 0 ? `
                <div class="winning-categories">
                    <h4><i class="fas fa-medal"></i> Categories You Win:</h4>
                    <div class="category-tags">
                        ${advantage.winning_categories.map(cat => `<span class="category-tag">${cat}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${insights.length > 0 ? `
                <div class="insights-section">
                    <h4><i class="fas fa-lightbulb"></i> Key Insights</h4>
                    <ul class="insights-list">
                        ${insights.map(insight => `<li>${insight}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            <div class="comparison-grid">
                <!-- Load Speed Comparison -->
                <div class="comparison-card">
                    <h4><i class="fas fa-tachometer-alt"></i> Load Speed</h4>
                    <div class="comparison-metrics">
                        <div class="metric-item ${comparison.load_speed?.winner === 'your_site' ? 'winner' : ''}">
                            <span class="metric-label">Your Site:</span>
                            <span class="metric-value">${yourSite.load_time || 'N/A'}s</span>
                        </div>
                        <div class="metric-item ${comparison.load_speed?.winner === 'competitor' ? 'winner' : ''}">
                            <span class="metric-label">Competitor:</span>
                            <span class="metric-value">${competitor.load_time || 'N/A'}s</span>
                        </div>
                    </div>
                    ${comparison.load_speed?.difference ? `
                        <div class="metric-difference">
                            ${comparison.load_speed.winner === 'your_site' ? '✅' : '⚠️'} 
                            ${Math.abs(comparison.load_speed.difference).toFixed(2)}s difference
                        </div>
                    ` : ''}
                </div>
                
                <!-- Errors Comparison -->
                <div class="comparison-card">
                    <h4><i class="fas fa-exclamation-triangle"></i> Errors</h4>
                    <div class="comparison-metrics">
                        <div class="metric-item ${comparison.errors?.winner === 'your_site' ? 'winner' : ''}">
                            <span class="metric-label">Your Site:</span>
                            <span class="metric-value ${yourSite.error_count > 0 ? 'error' : 'success'}">${yourSite.error_count || 0}</span>
                        </div>
                        <div class="metric-item ${comparison.errors?.winner === 'competitor' ? 'winner' : ''}">
                            <span class="metric-label">Competitor:</span>
                            <span class="metric-value ${competitor.error_count > 0 ? 'error' : 'success'}">${competitor.error_count || 0}</span>
                        </div>
                    </div>
                </div>
                
                <!-- SEO Score Comparison -->
                <div class="comparison-card">
                    <h4><i class="fas fa-star"></i> SEO Score</h4>
                    <div class="comparison-metrics">
                        <div class="metric-item ${comparison.seo_score?.winner === 'your_site' ? 'winner' : ''}">
                            <span class="metric-label">Your Site:</span>
                            <span class="metric-value">${yourSite.seo_score || 0}/100</span>
                        </div>
                        <div class="metric-item ${comparison.seo_score?.winner === 'competitor' ? 'winner' : ''}">
                            <span class="metric-label">Competitor:</span>
                            <span class="metric-value">${competitor.seo_score || 0}/100</span>
                        </div>
                    </div>
                    ${comparison.seo_score?.difference ? `
                        <div class="metric-difference">
                            ${comparison.seo_score.difference > 0 ? '✅' : '⚠️'} 
                            ${Math.abs(comparison.seo_score.difference)} point difference
                        </div>
                    ` : ''}
                </div>
            </div>
            
            <!-- Detailed Scores Breakdown -->
            <div class="comparison-section">
                <h3><i class="fas fa-chart-bar"></i> Detailed Score Breakdown</h3>
                <div class="score-breakdown-grid">
                    <div class="breakdown-card">
                        <h5>SEO Score Components</h5>
                        <div class="breakdown-item">
                            <span>Your Site:</span>
                            <div class="breakdown-bar">
                                <div class="breakdown-fill" style="width: ${yourSite.seo_score || 0}%; background: ${(yourSite.seo_score || 0) >= 80 ? '#28a745' : (yourSite.seo_score || 0) >= 60 ? '#ffc107' : '#dc3545'}"></div>
                                <span class="breakdown-value">${yourSite.seo_score || 0}/100</span>
                            </div>
                        </div>
                        <div class="breakdown-item">
                            <span>Competitor:</span>
                            <div class="breakdown-bar">
                                <div class="breakdown-fill" style="width: ${competitor.seo_score || 0}%; background: ${(competitor.seo_score || 0) >= 80 ? '#28a745' : (competitor.seo_score || 0) >= 60 ? '#ffc107' : '#dc3545'}"></div>
                                <span class="breakdown-value">${competitor.seo_score || 0}/100</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="breakdown-card">
                        <h5>Performance Score</h5>
                        <div class="breakdown-item">
                            <span>Your Site:</span>
                            <div class="breakdown-bar">
                                <div class="breakdown-fill" style="width: ${yourSite.performance_score || 0}%"></div>
                                <span class="breakdown-value">${yourSite.performance_score || 0}/100</span>
                            </div>
                        </div>
                        <div class="breakdown-item">
                            <span>Competitor:</span>
                            <div class="breakdown-bar">
                                <div class="breakdown-fill" style="width: ${competitor.performance_score || 0}%"></div>
                                <span class="breakdown-value">${competitor.performance_score || 0}/100</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="breakdown-card">
                        <h5>Technical Score</h5>
                        <div class="breakdown-item">
                            <span>Your Site:</span>
                            <div class="breakdown-bar">
                                <div class="breakdown-fill" style="width: ${yourSite.technical_score || 0}%"></div>
                                <span class="breakdown-value">${yourSite.technical_score || 0}/100</span>
                            </div>
                        </div>
                        <div class="breakdown-item">
                            <span>Competitor:</span>
                            <div class="breakdown-bar">
                                <div class="breakdown-fill" style="width: ${competitor.technical_score || 0}%"></div>
                                <span class="breakdown-value">${competitor.technical_score || 0}/100</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- On-Page SEO Comparison -->
            <div class="comparison-section">
                <h3><i class="fas fa-code"></i> On-Page SEO Comparison</h3>
                <div class="on-page-grid">
                    <div class="on-page-item">
                        <h5>Title Tag</h5>
                        <div class="side-by-side">
                            <div class="side-item">
                                <strong>Your Site:</strong>
                                <p class="text-content">${yourSite.title || 'N/A'}</p>
                                <span class="badge ${(yourSite.title_length || 0) >= 30 && (yourSite.title_length || 0) <= 60 ? 'badge-success' : 'badge-warning'}">${yourSite.title_length || 0} chars</span>
                            </div>
                            <div class="side-item">
                                <strong>Competitor:</strong>
                                <p class="text-content">${competitor.title || 'N/A'}</p>
                                <span class="badge ${(competitor.title_length || 0) >= 30 && (competitor.title_length || 0) <= 60 ? 'badge-success' : 'badge-warning'}">${competitor.title_length || 0} chars</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="on-page-item">
                        <h5>Meta Description</h5>
                        <div class="side-by-side">
                            <div class="side-item">
                                <strong>Your Site:</strong>
                                <p class="text-content">${yourSite.meta_description || 'N/A'}</p>
                                <span class="badge ${(yourSite.meta_description_length || 0) >= 120 && (yourSite.meta_description_length || 0) <= 160 ? 'badge-success' : 'badge-warning'}">${yourSite.meta_description_length || 0} chars</span>
                            </div>
                            <div class="side-item">
                                <strong>Competitor:</strong>
                                <p class="text-content">${competitor.meta_description || 'N/A'}</p>
                                <span class="badge ${(competitor.meta_description_length || 0) >= 120 && (competitor.meta_description_length || 0) <= 160 ? 'badge-success' : 'badge-warning'}">${competitor.meta_description_length || 0} chars</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="on-page-item">
                        <h5>Headings Structure</h5>
                        <div class="side-by-side">
                            <div class="side-item">
                                <strong>Your Site:</strong>
                                <p>H1: ${yourSite.h1_count || 0} ${yourSite.h1_count === 1 ? '✅' : yourSite.h1_count === 0 ? '❌' : '⚠️'}</p>
                                <p>H2: ${yourSite.h2_count || 0}, H3: ${yourSite.h3_count || 0}</p>
                                <p>H4-H6: ${(yourSite.h4_count || 0) + (yourSite.h5_count || 0) + (yourSite.h6_count || 0)}</p>
                            </div>
                            <div class="side-item">
                                <strong>Competitor:</strong>
                                <p>H1: ${competitor.h1_count || 0} ${competitor.h1_count === 1 ? '✅' : competitor.h1_count === 0 ? '❌' : '⚠️'}</p>
                                <p>H2: ${competitor.h2_count || 0}, H3: ${competitor.h3_count || 0}</p>
                                <p>H4-H6: ${(competitor.h4_count || 0) + (competitor.h5_count || 0) + (competitor.h6_count || 0)}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="on-page-item">
                        <h5>Content Analysis</h5>
                        <div class="side-by-side">
                            <div class="side-item">
                                <strong>Your Site:</strong>
                                <p><strong>Words:</strong> ${(yourSite.word_count || 0).toLocaleString()}</p>
                                <p><strong>Characters:</strong> ${(yourSite.character_count || 0).toLocaleString()}</p>
                                <p><strong>Paragraphs:</strong> ${yourSite.paragraph_count || 0}</p>
                                <p><strong>Readability:</strong> ${yourSite.readability_score || 0} (${yourSite.readability_grade || 'N/A'})</p>
                            </div>
                            <div class="side-item">
                                <strong>Competitor:</strong>
                                <p><strong>Words:</strong> ${(competitor.word_count || 0).toLocaleString()}</p>
                                <p><strong>Characters:</strong> ${(competitor.character_count || 0).toLocaleString()}</p>
                                <p><strong>Paragraphs:</strong> ${competitor.paragraph_count || 0}</p>
                                <p><strong>Readability:</strong> ${competitor.readability_score || 0} (${competitor.readability_grade || 'N/A'})</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="on-page-item">
                        <h5>Images & Media</h5>
                        <div class="side-by-side">
                            <div class="side-item">
                                <strong>Your Site:</strong>
                                <p>Total: ${yourSite.images_count || 0}</p>
                                <p>With Alt: ${yourSite.images_with_alt || 0}</p>
                                <p>Alt Coverage: ${yourSite.images_alt_coverage || 0}% ${(yourSite.images_alt_coverage || 0) === 100 ? '✅' : '⚠️'}</p>
                            </div>
                            <div class="side-item">
                                <strong>Competitor:</strong>
                                <p>Total: ${competitor.images_count || 0}</p>
                                <p>With Alt: ${competitor.images_with_alt || 0}</p>
                                <p>Alt Coverage: ${competitor.images_alt_coverage || 0}% ${(competitor.images_alt_coverage || 0) === 100 ? '✅' : '⚠️'}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="on-page-item">
                        <h5>Technical SEO</h5>
                        <div class="side-by-side">
                            <div class="side-item">
                                <strong>Your Site:</strong>
                                <p>Canonical: ${yourSite.canonical_url ? '✅ Yes' : '❌ No'}</p>
                                <p>OG Tags: ${yourSite.og_tags_count || 0}</p>
                                <p>Twitter Tags: ${yourSite.twitter_tags_count || 0}</p>
                                <p>Schema: ${yourSite.schema_count || 0} types</p>
                                <p>Language: ${yourSite.language || 'Not set'}</p>
                            </div>
                            <div class="side-item">
                                <strong>Competitor:</strong>
                                <p>Canonical: ${competitor.canonical_url ? '✅ Yes' : '❌ No'}</p>
                                <p>OG Tags: ${competitor.og_tags_count || 0}</p>
                                <p>Twitter Tags: ${competitor.twitter_tags_count || 0}</p>
                                <p>Schema: ${competitor.schema_count || 0} types</p>
                                <p>Language: ${competitor.language || 'Not set'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Details -->
            <div class="comparison-section">
                <h3><i class="fas fa-tachometer-alt"></i> Performance Details</h3>
                <div class="performance-details-grid">
                    <div class="performance-detail-item">
                        <h5>Page Size</h5>
                        <p>Your Site: <strong>${(yourSite.page_size / 1024).toFixed(2)} KB</strong></p>
                        <p>Competitor: <strong>${(competitor.page_size / 1024).toFixed(2)} KB</strong></p>
                        <p>HTML Size: ${(yourSite.html_size / 1024).toFixed(2)} KB vs ${(competitor.html_size / 1024).toFixed(2)} KB</p>
                    </div>
                    
                    <div class="performance-detail-item">
                        <h5>Resources</h5>
                        <p>Scripts: ${yourSite.scripts_count || 0} vs ${competitor.scripts_count || 0}</p>
                        <p>Stylesheets: ${yourSite.stylesheets_count || 0} vs ${competitor.stylesheets_count || 0}</p>
                        <p>Render-Blocking: ${yourSite.render_blocking_resources || 0} vs ${competitor.render_blocking_resources || 0}</p>
                    </div>
                    
                    <div class="performance-detail-item">
                        <h5>Optimizations</h5>
                        <p>Async Scripts: ${yourSite.scripts_with_async || 0} vs ${competitor.scripts_with_async || 0}</p>
                        <p>Defer Scripts: ${yourSite.scripts_with_defer || 0} vs ${competitor.scripts_with_defer || 0}</p>
                        <p>Preconnect: ${yourSite.preconnect_count || 0} vs ${competitor.preconnect_count || 0}</p>
                    </div>
                </div>
            </div>
            
            <!-- Mobile & Security -->
            <div class="comparison-section">
                <h3><i class="fas fa-mobile-alt"></i> Mobile & Security</h3>
                <div class="mobile-security-grid">
                    <div class="mobile-security-item">
                        <h5>Mobile-Friendliness</h5>
                        <div class="side-by-side">
                            <div class="side-item">
                                <strong>Your Site:</strong>
                                <p>Viewport: ${yourSite.has_viewport ? '✅' : '❌'}</p>
                                <p>Mobile Optimized: ${yourSite.has_mobile_optimized ? '✅' : '❌'}</p>
                                <p>Touch Icon: ${yourSite.has_touch_icon ? '✅' : '❌'}</p>
                                <p>Responsive Images: ${yourSite.images_with_srcset || 0}</p>
                            </div>
                            <div class="side-item">
                                <strong>Competitor:</strong>
                                <p>Viewport: ${competitor.has_viewport ? '✅' : '❌'}</p>
                                <p>Mobile Optimized: ${competitor.has_mobile_optimized ? '✅' : '❌'}</p>
                                <p>Touch Icon: ${competitor.has_touch_icon ? '✅' : '❌'}</p>
                                <p>Responsive Images: ${competitor.images_with_srcset || 0}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mobile-security-item">
                        <h5>Security Headers</h5>
                        <div class="side-by-side">
                            <div class="side-item">
                                <strong>Your Site:</strong>
                                <p>HTTPS: ${yourSite.security_headers?.https ? '✅' : '❌'}</p>
                                <p>Security Headers: ${yourSite.security_headers_count || 0}/7</p>
                                <p>HSTS: ${yourSite.security_headers?.strict_transport_security ? '✅' : '❌'}</p>
                                <p>CSP: ${yourSite.security_headers?.content_security_policy ? '✅' : '❌'}</p>
                            </div>
                            <div class="side-item">
                                <strong>Competitor:</strong>
                                <p>HTTPS: ${competitor.security_headers?.https ? '✅' : '❌'}</p>
                                <p>Security Headers: ${competitor.security_headers_count || 0}/7</p>
                                <p>HSTS: ${competitor.security_headers?.strict_transport_security ? '✅' : '❌'}</p>
                                <p>CSP: ${competitor.security_headers?.content_security_policy ? '✅' : '❌'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Keyword Comparison -->
            ${comparison.keywords ? `
                <div class="comparison-section">
                    <h3><i class="fas fa-key"></i> Keyword Analysis</h3>
                    
                    ${comparison.keywords.common_keywords && comparison.keywords.common_keywords.length > 0 ? `
                        <div class="keyword-group">
                            <h5>Common Keywords (${comparison.keywords.common_keywords.length})</h5>
                            <div class="keywords-list">
                                ${comparison.keywords.common_keywords.slice(0, 15).map(kw => `
                                    <span class="keyword-tag">
                                        ${kw.keyword} 
                                        <small>(You: ${kw.your_count}, Them: ${kw.competitor_count})</small>
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${comparison.keywords.unique_to_your_site && comparison.keywords.unique_to_your_site.length > 0 ? `
                        <div class="keyword-group">
                            <h5>Unique to Your Site (${comparison.keywords.unique_to_your_site.length})</h5>
                            <div class="keywords-list">
                                ${comparison.keywords.unique_to_your_site.slice(0, 15).map(kw => `
                                    <span class="keyword-tag unique-yours">
                                        ${kw.keyword} <small>(${kw.count}x)</small>
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${comparison.keywords.unique_to_competitor && comparison.keywords.unique_to_competitor.length > 0 ? `
                        <div class="keyword-group">
                            <h5>Unique to Competitor (${comparison.keywords.unique_to_competitor.length})</h5>
                            <div class="keywords-list">
                                ${comparison.keywords.unique_to_competitor.slice(0, 15).map(kw => `
                                    <span class="keyword-tag unique-competitor">
                                        ${kw.keyword} <small>(${kw.count}x)</small>
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            ` : ''}
            
            <!-- Backlink Indicators -->
            ${comparison.backlinks ? `
                <div class="comparison-section">
                    <h3><i class="fas fa-link"></i> Backlink & Social Indicators</h3>
                    <div class="backlink-detailed-grid">
                        <div class="backlink-detailed-item">
                            <h5>Your Site</h5>
                            <div class="backlink-metrics">
                                <p><strong>Backlink Potential Score:</strong> ${comparison.backlinks.your_site?.backlink_potential_score || 0}/100</p>
                                <p><strong>Social Platforms:</strong> ${comparison.backlinks.your_site?.social_count || 0}</p>
                                <p><strong>External Domains:</strong> ${comparison.backlinks.your_site?.external_domains_count || 0}</p>
                                <p><strong>Has Citations:</strong> ${comparison.backlinks.your_site?.has_citations ? '✅ Yes' : '❌ No'}</p>
                                ${comparison.backlinks.your_site?.social_platforms ? `
                                    <div class="social-platforms">
                                        ${Object.entries(comparison.backlinks.your_site.social_platforms).map(([platform, has]) => 
                                            `<span class="social-badge ${has ? 'active' : 'inactive'}">${platform}</span>`
                                        ).join('')}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        <div class="backlink-detailed-item">
                            <h5>Competitor</h5>
                            <div class="backlink-metrics">
                                <p><strong>Backlink Potential Score:</strong> ${comparison.backlinks.competitor?.backlink_potential_score || 0}/100</p>
                                <p><strong>Social Platforms:</strong> ${comparison.backlinks.competitor?.social_count || 0}</p>
                                <p><strong>External Domains:</strong> ${comparison.backlinks.competitor?.external_domains_count || 0}</p>
                                <p><strong>Has Citations:</strong> ${comparison.backlinks.competitor?.has_citations ? '✅ Yes' : '❌ No'}</p>
                                ${comparison.backlinks.competitor?.social_platforms ? `
                                    <div class="social-platforms">
                                        ${Object.entries(comparison.backlinks.competitor.social_platforms).map(([platform, has]) => 
                                            `<span class="social-badge ${has ? 'active' : 'inactive'}">${platform}</span>`
                                        ).join('')}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            ` : ''}
            
            <!-- Link Analysis - Always Show (NEW FEATURE) -->
            <div class="comparison-section">
                <h3><i class="fas fa-sitemap"></i> Link Analysis</h3>
                <div class="link-analysis-grid">
                    ${yourSite.link_analysis ? `
                        <div class="link-analysis-item">
                            <h4>Your Site</h4>
                            <p><strong>Internal Links:</strong> ${yourSite.link_analysis.link_metrics?.internal_links_count || 0}</p>
                            <p><strong>External Links:</strong> ${yourSite.link_analysis.link_metrics?.external_links_count || 0}</p>
                            ${yourSite.link_analysis.anchor_analysis ? `
                                <p><strong>Keyword-Rich Anchors:</strong> ${yourSite.link_analysis.anchor_analysis.keyword_rich || 0} (${Math.round((yourSite.link_analysis.anchor_analysis.keyword_rich_ratio || 0) * 100)}%)</p>
                                <p><strong>Generic Anchors:</strong> ${yourSite.link_analysis.anchor_analysis.generic || 0}</p>
                            ` : ''}
                        </div>
                    ` : '<div class="link-analysis-item"><p>Link analysis data not available</p></div>'}
                    ${competitor.link_analysis ? `
                        <div class="link-analysis-item">
                            <h4>Competitor</h4>
                            <p><strong>Internal Links:</strong> ${competitor.link_analysis.link_metrics?.internal_links_count || 0}</p>
                            <p><strong>External Links:</strong> ${competitor.link_analysis.link_metrics?.external_links_count || 0}</p>
                            ${competitor.link_analysis.anchor_analysis ? `
                                <p><strong>Keyword-Rich Anchors:</strong> ${competitor.link_analysis.anchor_analysis.keyword_rich || 0} (${Math.round((competitor.link_analysis.anchor_analysis.keyword_rich_ratio || 0) * 100)}%)</p>
                                <p><strong>Generic Anchors:</strong> ${competitor.link_analysis.anchor_analysis.generic || 0}</p>
                            ` : ''}
                        </div>
                    ` : '<div class="link-analysis-item"><p>Link analysis data not available</p></div>'}
                </div>
            </div>
            
            <!-- Content Gaps - Always Show -->
            ${data.content_gaps ? `
                <div class="comparison-section content-gaps-section">
                    <h3><i class="fas fa-gap"></i> Content Gap Analysis</h3>
                    <div class="content-gaps-grid">
                        <div class="gap-item">
                            <h4>Missing Topics (${data.content_gaps.missing_topics?.length || 0})</h4>
                            <p>Topics competitor covers that you don't:</p>
                            <div class="topic-tags">
                                ${(data.content_gaps.missing_topics || []).slice(0, 15).map(topic => 
                                    `<span class="topic-tag missing">${topic}</span>`
                                ).join('') || '<p>No missing topics found</p>'}
                            </div>
                        </div>
                        <div class="gap-item">
                            <h4>Your Unique Topics (${data.content_gaps.unique_topics?.length || 0})</h4>
                            <p>Topics you cover that competitor doesn't:</p>
                            <div class="topic-tags">
                                ${(data.content_gaps.unique_topics || []).slice(0, 15).map(topic => 
                                    `<span class="topic-tag unique">${topic}</span>`
                                ).join('') || '<p>No unique topics found</p>'}
                            </div>
                        </div>
                    </div>
                    ${data.content_gaps.recommendations && data.content_gaps.recommendations.length > 0 ? `
                        <div class="content-recommendations">
                            <h4>Content Recommendations</h4>
                            <ul>
                                ${data.content_gaps.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            ` : ''}
            
            <!-- Accessibility - Always Show -->
            <div class="comparison-section">
                <h3><i class="fas fa-universal-access"></i> Accessibility Analysis</h3>
                <div class="accessibility-grid">
                    ${yourSite.accessibility ? `
                        <div class="accessibility-item">
                            <h4>Your Site</h4>
                            <div class="accessibility-score">
                                <div class="score-circle-large" style="background: ${getScoreColor(yourSite.accessibility.wcag_score || 0)}">
                                    <span class="score-large">${yourSite.accessibility.wcag_score || 0}</span>
                                </div>
                                <p>WCAG ${yourSite.accessibility.wcag_level || 'N/A'}</p>
                            </div>
                            <p><strong>Image Alt Coverage:</strong> ${yourSite.accessibility.image_analysis?.alt_coverage || 0}%</p>
                            <p><strong>Form Label Coverage:</strong> ${yourSite.accessibility.form_analysis?.label_coverage || 0}%</p>
                            <p><strong>Semantic HTML Score:</strong> ${yourSite.accessibility.semantic_analysis?.score || 0}/100</p>
                        </div>
                    ` : '<div class="accessibility-item"><p>Accessibility data not available</p></div>'}
                    ${competitor.accessibility ? `
                        <div class="accessibility-item">
                            <h4>Competitor</h4>
                            <div class="accessibility-score">
                                <div class="score-circle-large" style="background: ${getScoreColor(competitor.accessibility.wcag_score || 0)}">
                                    <span class="score-large">${competitor.accessibility.wcag_score || 0}</span>
                                </div>
                                <p>WCAG ${competitor.accessibility.wcag_level || 'N/A'}</p>
                            </div>
                            <p><strong>Image Alt Coverage:</strong> ${competitor.accessibility.image_analysis?.alt_coverage || 0}%</p>
                            <p><strong>Form Label Coverage:</strong> ${competitor.accessibility.form_analysis?.label_coverage || 0}%</p>
                            <p><strong>Semantic HTML Score:</strong> ${competitor.accessibility.semantic_analysis?.score || 0}/100</p>
                        </div>
                    ` : '<div class="accessibility-item"><p>Accessibility data not available</p></div>'}
                </div>
            </div>
            
            <!-- Export Buttons -->
            <div class="comparison-section" style="text-align: center; padding: 20px;">
                <h3><i class="fas fa-download"></i> Export Results</h3>
                <div class="export-buttons">
                    <button class="btn btn-secondary" onclick="exportAnalysis('csv', ${JSON.stringify(data).replace(/"/g, '&quot;')})">
                        <i class="fas fa-file-csv"></i> Export CSV
                    </button>
                    <button class="btn btn-secondary" onclick="exportAnalysis('json', ${JSON.stringify(data).replace(/"/g, '&quot;')})">
                        <i class="fas fa-file-code"></i> Export JSON
                    </button>
                    <button class="btn btn-secondary" onclick="exportAnalysis('txt', ${JSON.stringify(data).replace(/"/g, '&quot;')})">
                        <i class="fas fa-file-alt"></i> Export Report
                    </button>
                </div>
            </div>
            
            <!-- Google PageSpeed Insights -->
            ${yourSite.pagespeed_mobile || competitor.pagespeed_mobile ? `
                <div class="comparison-section">
                    <h3><i class="fas fa-tachometer-alt"></i> Google PageSpeed Insights</h3>
                    <div class="pagespeed-grid">
                        ${yourSite.pagespeed_mobile && !yourSite.pagespeed_mobile.has_error ? `
                            <div class="pagespeed-card">
                                <h4>Your Site - Mobile</h4>
                                <div class="pagespeed-scores">
                                    <div class="score-item">
                                        <span class="score-label">Performance</span>
                                        <div class="score-circle" style="background: ${getScoreColor(yourSite.pagespeed_mobile.scores.performance)}">
                                            ${yourSite.pagespeed_mobile.scores.performance}
                                        </div>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">Accessibility</span>
                                        <div class="score-circle" style="background: ${getScoreColor(yourSite.pagespeed_mobile.scores.accessibility)}">
                                            ${yourSite.pagespeed_mobile.scores.accessibility}
                                        </div>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">Best Practices</span>
                                        <div class="score-circle" style="background: ${getScoreColor(yourSite.pagespeed_mobile.scores.best_practices)}">
                                            ${yourSite.pagespeed_mobile.scores.best_practices}
                                        </div>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">SEO</span>
                                        <div class="score-circle" style="background: ${getScoreColor(yourSite.pagespeed_mobile.scores.seo)}">
                                            ${yourSite.pagespeed_mobile.scores.seo}
                                        </div>
                                    </div>
                                </div>
                                ${yourSite.pagespeed_mobile.core_web_vitals ? `
                                    <div class="core-web-vitals">
                                        <h5>Core Web Vitals</h5>
                                        <p>LCP: ${yourSite.pagespeed_mobile.core_web_vitals.lcp.value}s (${yourSite.pagespeed_mobile.core_web_vitals.lcp.category})</p>
                                        <p>FID: ${yourSite.pagespeed_mobile.core_web_vitals.fid.value}s (${yourSite.pagespeed_mobile.core_web_vitals.fid.category})</p>
                                        <p>CLS: ${yourSite.pagespeed_mobile.core_web_vitals.cls.value} (${yourSite.pagespeed_mobile.core_web_vitals.cls.category})</p>
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}
                        ${competitor.pagespeed_mobile && !competitor.pagespeed_mobile.has_error ? `
                            <div class="pagespeed-card">
                                <h4>Competitor - Mobile</h4>
                                <div class="pagespeed-scores">
                                    <div class="score-item">
                                        <span class="score-label">Performance</span>
                                        <div class="score-circle" style="background: ${getScoreColor(competitor.pagespeed_mobile.scores.performance)}">
                                            ${competitor.pagespeed_mobile.scores.performance}
                                        </div>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">Accessibility</span>
                                        <div class="score-circle" style="background: ${getScoreColor(competitor.pagespeed_mobile.scores.accessibility)}">
                                            ${competitor.pagespeed_mobile.scores.accessibility}
                                        </div>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">Best Practices</span>
                                        <div class="score-circle" style="background: ${getScoreColor(competitor.pagespeed_mobile.scores.best_practices)}">
                                            ${competitor.pagespeed_mobile.scores.best_practices}
                                        </div>
                                    </div>
                                    <div class="score-item">
                                        <span class="score-label">SEO</span>
                                        <div class="score-circle" style="background: ${getScoreColor(competitor.pagespeed_mobile.scores.seo)}">
                                            ${competitor.pagespeed_mobile.scores.seo}
                                        </div>
                                    </div>
                                </div>
                                ${competitor.pagespeed_mobile.core_web_vitals ? `
                                    <div class="core-web-vitals">
                                        <h5>Core Web Vitals</h5>
                                        <p>LCP: ${competitor.pagespeed_mobile.core_web_vitals.lcp.value}s (${competitor.pagespeed_mobile.core_web_vitals.lcp.category})</p>
                                        <p>FID: ${competitor.pagespeed_mobile.core_web_vitals.fid.value}s (${competitor.pagespeed_mobile.core_web_vitals.fid.category})</p>
                                        <p>CLS: ${competitor.pagespeed_mobile.core_web_vitals.cls.value} (${competitor.pagespeed_mobile.core_web_vitals.cls.category})</p>
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
            
            <!-- Visual Screenshots -->
            ${yourSite.desktop_screenshot && competitor.desktop_screenshot && 
              !yourSite.desktop_screenshot.has_error && !competitor.desktop_screenshot.has_error ? `
                <div class="comparison-section">
                    <h3><i class="fas fa-image"></i> Visual Comparison</h3>
                    <div class="screenshot-comparison">
                        <div class="screenshot-item">
                            <h4>Your Site</h4>
                            <img src="data:image/png;base64,${yourSite.desktop_screenshot.screenshot}" 
                                 alt="Your site screenshot" 
                                 class="screenshot-image"
                                 onclick="openScreenshotModal('data:image/png;base64,${yourSite.desktop_screenshot.screenshot}', 'Your Site')">
                        </div>
                        <div class="screenshot-item">
                            <h4>Competitor</h4>
                            <img src="data:image/png;base64,${competitor.desktop_screenshot.screenshot}" 
                                 alt="Competitor screenshot" 
                                 class="screenshot-image"
                                 onclick="openScreenshotModal('data:image/png;base64,${competitor.desktop_screenshot.screenshot}', 'Competitor')">
                        </div>
                    </div>
                    ${data.visual_comparison && !data.visual_comparison.has_error ? `
                        <p class="visual-similarity">
                            Visual Similarity: ${data.visual_comparison.similarity_percentage}%
                        </p>
                    ` : ''}
                </div>
            ` : ''}
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Helper function for score colors
function getScoreColor(score) {
    if (score >= 90) return '#28a745';
    if (score >= 50) return '#ffc107';
    return '#dc3545';
}

// Export analysis
async function exportAnalysis(format, data) {
    try {
        const response = await fetch('/api/export-competitor-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: data,
                format: format
            })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `competitor_analysis.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Export error:', error);
        alert('Export failed: ' + error.message);
    }
}

// Screenshot modal
function openScreenshotModal(imageSrc, title) {
    const modal = document.createElement('div');
    modal.className = 'screenshot-modal';
    modal.innerHTML = `
        <div class="screenshot-modal-content">
            <span class="screenshot-modal-close" onclick="this.parentElement.parentElement.remove()">&times;</span>
            <h3>${title}</h3>
            <img src="${imageSrc}" alt="${title}" style="max-width: 100%; height: auto;">
        </div>
    `;
    document.body.appendChild(modal);
    modal.onclick = function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    };
}

// Initialize Socket.IO connection
document.addEventListener('DOMContentLoaded', function() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('progress', function(data) {
        updateProgress(data);
    });
    
    // Form submission
    const form = document.getElementById('crawlForm');
    form.addEventListener('submit', handleFormSubmit);
});

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const url = document.getElementById('url').value;
    const maxDepth = document.getElementById('max_depth').value;
    const startBtn = document.getElementById('startBtn');
    
    // Disable button
    startBtn.disabled = true;
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
    
    // Auto-fix URL (add https:// if missing)
    let fixedUrl = url.trim();
    if (!fixedUrl.match(/^https?:\/\//i)) {
        fixedUrl = 'https://' + fixedUrl;
    }
    
    try {
        const response = await fetch('/api/start-crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: fixedUrl,
                max_depth: parseInt(maxDepth),
                output_dir: 'output', // Fixed output directory
                clear_cache: document.getElementById('clear_cache').checked
            })
        });
        
        // Check if response is actually JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response:', text.substring(0, 200));
            throw new Error(`Server returned non-JSON response. Status: ${response.status}. Please check server logs.`);
        }
        
        const data = await response.json();
        
        if (response.ok && data.job_id) {
            currentJobId = data.job_id;
            console.log('Crawl started with job_id:', data.job_id);
            showProgressCard();
            
            // Immediately check status once, then start polling
            // This helps catch any immediate issues
            setTimeout(async () => {
                try {
                    const statusResponse = await fetch(`/api/crawl-status/${data.job_id}`);
                    const statusData = await statusResponse.json();
                    
                    if (statusData.status === 'not_found' || statusData.error) {
                        showError(statusData.message || 'Job was not found. Please try again.');
                        return;
                    }
                    
                    // If job exists, start polling
                    startPolling(data.job_id);
                } catch (error) {
                    console.error('Error checking initial status:', error);
                    // Still try to start polling
                    startPolling(data.job_id);
                }
            }, 1000); // Wait 1 second for job to be fully initialized
        } else {
            alert('Error: ' + data.error);
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start Crawling';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error starting crawl: ' + error.message);
        startBtn.disabled = false;
        startBtn.innerHTML = '<i class="fas fa-play"></i> Start Crawling';
    }
}

// Show progress card
function showProgressCard() {
    document.getElementById('progressCard').style.display = 'block';
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressText').textContent = '0%';
    const progressMessageText = document.getElementById('progressMessageText');
    const loadingIcon = document.getElementById('loadingIcon');
    if (progressMessageText) progressMessageText.textContent = 'Initializing...';
    if (loadingIcon) loadingIcon.style.display = 'inline-block';
}

// Update progress
function updateProgress(data) {
    if (data.job_id !== currentJobId) return;
    
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressMessageText = document.getElementById('progressMessageText');
    const loadingIcon = document.getElementById('loadingIcon');
    const stats = document.getElementById('stats');
    const errorContainer = document.getElementById('errorContainer');
    
    // Update progress bar with smooth animation
    const progress = data.progress || 0;
    progressFill.style.width = progress + '%';
    progressText.textContent = progress + '%';
    
    // Update message
    if (data.message) {
        progressMessageText.textContent = data.message;
        
        // Show/hide loading icon based on status
        if (data.status === 'completed' || data.status === 'error') {
            if (loadingIcon) loadingIcon.style.display = 'none';
        } else {
            if (loadingIcon) loadingIcon.style.display = 'inline-block';
        }
    }
    
    // Update stats
    if (data.pages_crawled !== undefined || data.links_found !== undefined) {
        stats.style.display = 'flex';
        if (data.pages_crawled !== undefined) {
            document.getElementById('pagesCount').textContent = data.pages_crawled;
        }
        if (data.links_found !== undefined) {
            document.getElementById('linksCount').textContent = data.links_found;
        }
        // Show internal/external links if available
        if (data.internal_links !== undefined) {
            const internalItem = document.getElementById('internalLinksItem');
            const internalCount = document.getElementById('internalLinksCount');
            if (internalItem && internalCount) {
                internalItem.style.display = 'flex';
                internalCount.textContent = data.internal_links;
            }
        }
        if (data.external_links !== undefined) {
            const externalItem = document.getElementById('externalLinksItem');
            const externalCount = document.getElementById('externalLinksCount');
            if (externalItem && externalCount) {
                externalItem.style.display = 'flex';
                externalCount.textContent = data.external_links;
            }
        }
    }
    
    // Update current page info
    if (data.current_page) {
        const currentPageInfo = document.getElementById('currentPageInfo');
        const currentPageText = document.getElementById('currentPageText');
        if (currentPageInfo && currentPageText) {
            currentPageInfo.style.display = 'block';
            const pageDisplay = data.current_page.length > 60 
                ? data.current_page.substring(0, 60) + '...' 
                : data.current_page;
            currentPageText.textContent = `Current: ${pageDisplay}`;
        }
    }
    
    // Handle errors
    if (data.status === 'error') {
        errorContainer.style.display = 'block';
        errorContainer.innerHTML = '<strong>Error:</strong> ' + data.message;
        if (loadingIcon) loadingIcon.style.display = 'none';
    } else {
        errorContainer.style.display = 'none';
    }
    
    // Handle completion
    if (data.status === 'completed') {
        if (loadingIcon) loadingIcon.style.display = 'none';
        
        // Reset button state
        const startBtn = document.getElementById('startBtn');
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start Crawling';
        }
        
        setTimeout(() => {
            showResultsCard(data.job_id);
        }, 1000);
    }
    
    // Handle errors - also reset button
    if (data.status === 'error') {
        const startBtn = document.getElementById('startBtn');
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play"></i> Start Crawling';
        }
    }
}

// Show results card
function showResultsCard(jobId) {
    document.getElementById('progressCard').style.display = 'none';
    document.getElementById('resultsCard').style.display = 'block';
    
    // Set up download buttons
    const baseUrl = `/api/download/${jobId}`;
    document.getElementById('downloadJsonBtn').onclick = () => {
        window.location.href = baseUrl + '/json';
    };
    document.getElementById('downloadCsvBtn').onclick = () => {
        window.location.href = baseUrl + '/csv';
    };
    document.getElementById('downloadSitemapBtn').onclick = () => {
        window.location.href = baseUrl + '/sitemap';
    };
    
    // Set up view results button
    document.getElementById('viewResultsBtn').href = `/results/${jobId}`;
}

// Poll for status updates
function startPolling(jobId) {
    let pollCount = 0;
    const maxPolls = 300; // Stop after 10 minutes (300 * 2 seconds)
    
    const pollInterval = setInterval(async () => {
        pollCount++;
        
        try {
            const response = await fetch(`/api/crawl-status/${jobId}`);
            
            if (!response.ok && response.status === 404) {
                // Job not found - stop polling and show error
                clearInterval(pollInterval);
                showError('Crawl job not found. Please try starting a new crawl.');
                return;
            }
            
            const data = await response.json();
            
            // Handle job not found status
            if (data.status === 'not_found' || data.error) {
                clearInterval(pollInterval);
                showError(data.message || 'Crawl job not found. Please try starting a new crawl.');
                return;
            }
            
            // Update progress if available
            if (data.progress !== undefined) {
                updateProgress(data);
            }
            
            // Stop polling if crawl is done
            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(pollInterval);
                if (data.status === 'completed') {
                    showResultsCard(jobId);
                } else if (data.status === 'error') {
                    showError(data.message || 'Crawl failed. Please try again.');
                }
            }
            
            // Stop polling after max attempts
            if (pollCount >= maxPolls) {
                clearInterval(pollInterval);
                showError('Crawl is taking longer than expected. Please check the results page or try again.');
            }
        } catch (error) {
            console.error('Error polling status:', error);
            // Don't stop polling on network errors, but stop after too many failures
            if (pollCount >= 10) {
                clearInterval(pollInterval);
                showError('Unable to check crawl status. Please refresh the page.');
            }
        }
    }, 2000); // Poll every 2 seconds
}

// Show error message
function showError(message) {
    const progressCard = document.getElementById('progressCard');
    const errorContainer = document.getElementById('errorContainer');
    
    if (errorContainer) {
        errorContainer.style.display = 'block';
        errorContainer.innerHTML = `<strong>Error:</strong> ${message}`;
    }
    
    // Update progress message
    const progressMessageText = document.getElementById('progressMessageText');
    const loadingIcon = document.getElementById('loadingIcon');
    if (progressMessageText) {
        progressMessageText.textContent = message;
        progressMessageText.style.color = '#dc3545';
    }
    if (loadingIcon) loadingIcon.style.display = 'none';
    
    // Hide progress bar
    const progressFill = document.getElementById('progressFill');
    if (progressFill) {
        progressFill.style.width = '0%';
    }
    
    const progressText = document.getElementById('progressText');
    if (progressText) {
        progressText.textContent = 'Error';
    }
    
    // Reset button
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        startBtn.disabled = false;
        startBtn.innerHTML = '<i class="fas fa-play"></i> Start Crawling';
    }
}

