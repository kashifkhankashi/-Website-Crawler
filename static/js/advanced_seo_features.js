/**
 * Advanced SEO Features Display Functions
 * 
 * This file contains all display functions for the new advanced SEO audit features:
 * - Core Web Vitals
 * - Advanced Performance Metrics
 * - Security & Trust Signals
 * - Indexability & Crawlability
 * - Comprehensive SEO Scoring
 */

// Display Core Web Vitals
function displayCoreWebVitals(data) {
    console.log('displayCoreWebVitals called');
    const container = document.getElementById('coreWebVitalsContainer');
    if (!container) {
        console.error('Core Web Vitals container (#coreWebVitalsContainer) not found');
        return;
    }
    
    try {
        console.log('Container found, processing data...', data);
        
        // Always clear and set content immediately to prevent "stuck" state
        if (!data) {
            console.warn('No data provided');
            container.innerHTML = `
                <div class="info-message" style="padding: 40px; text-align: center;">
                    <i class="fas fa-info-circle" style="font-size: 48px; color: #6c757d; margin-bottom: 20px;"></i>
                    <h3>No Data Available</h3>
                    <p>No crawl data provided. Please run a crawl first.</p>
                </div>
            `;
            return;
        }
        
        if (!data.pages || !Array.isArray(data.pages)) {
            console.warn('Invalid data format, pages:', data.pages);
            container.innerHTML = `
                <div class="info-message" style="padding: 40px; text-align: center;">
                    <i class="fas fa-info-circle" style="font-size: 48px; color: #6c757d; margin-bottom: 20px;"></i>
                    <h3>Invalid Data Format</h3>
                    <p>Data format is incorrect. Expected data.pages array. Got: ${typeof data.pages}</p>
                </div>
            `;
            return;
        }
        
        console.log(`Processing ${data.pages.length} pages for Core Web Vitals`);
        
        // Collect CWV data from all pages
        const cwvData = [];
        data.pages.forEach(page => {
            const cwv = page.core_web_vitals;
            if (cwv && !cwv.error) {
                cwvData.push({
                url: page.url,
                title: page.title,
                lcp: cwv.lcp,
                cls: cwv.cls,
                inp: cwv.inp,
                ttfb: cwv.ttfb,
                fcp: cwv.fcp,
                lcp_score: cwv.lcp_score,
                cls_score: cwv.cls_score,
                inp_score: cwv.inp_score,
                ttfb_score: cwv.ttfb_score,
                lcp_element: cwv.lcp_element,
                lcp_issues: cwv.lcp_issues || [],
                cls_issues: cwv.cls_issues || []
                });
            }
        });
        
        if (cwvData.length === 0) {
            container.innerHTML = `
                <div class="info-message" style="padding: 40px; text-align: center; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                    <i class="fas fa-info-circle" style="font-size: 48px; color: #6c757d; margin-bottom: 20px;"></i>
                    <h3 style="margin-bottom: 15px; color: #495057;">Core Web Vitals Data Not Available</h3>
                    <p style="color: #6c757d; line-height: 1.6; max-width: 600px; margin: 0 auto;">
                        Core Web Vitals metrics require Playwright browser automation, which is disabled by default for performance reasons.
                    </p>
                    <p style="color: #6c757d; line-height: 1.6; max-width: 600px; margin: 15px auto 0;">
                        <strong>To enable Core Web Vitals collection:</strong><br>
                        Set <code>use_playwright_for_cwv: true</code> in your crawl configuration. Note: This will significantly slow down crawling.
                    </p>
                </div>
            `;
            return;
        }
        
        // Calculate averages (handle division by zero)
        const avgLCP = cwvData.length > 0 ? cwvData.reduce((sum, p) => sum + (p.lcp || 0), 0) / cwvData.length : 0;
        const avgCLS = cwvData.length > 0 ? cwvData.reduce((sum, p) => sum + (p.cls || 0), 0) / cwvData.length : 0;
        const pagesWithINP = cwvData.filter(p => p.inp !== null && p.inp !== undefined);
        const avgINP = pagesWithINP.length > 0 ? 
            pagesWithINP.reduce((sum, p) => sum + p.inp, 0) / pagesWithINP.length : null;
        const pagesWithTTFB = cwvData.filter(p => p.ttfb !== null && p.ttfb !== undefined);
        const avgTTFB = pagesWithTTFB.length > 0 ?
            pagesWithTTFB.reduce((sum, p) => sum + p.ttfb, 0) / pagesWithTTFB.length : null;
        
        // Count scores
        const lcpGood = cwvData.filter(p => p.lcp_score === 'good').length;
        const clsGood = cwvData.filter(p => p.cls_score === 'good').length;
        const inpGood = cwvData.filter(p => p.inp_score === 'good').length;
    
    let html = `
        <div class="cwv-summary">
            <div class="cwv-metrics-grid">
                <div class="cwv-metric-card">
                    <div class="cwv-metric-header">
                        <h3><i class="fas fa-paint-brush"></i> LCP</h3>
                        <span class="cwv-label">Largest Contentful Paint</span>
                    </div>
                    <div class="cwv-metric-value">${avgLCP ? avgLCP.toFixed(2) + 's' : 'N/A'}</div>
                    <div class="cwv-metric-score ${getScoreClass(lcpGood, cwvData.length)}">
                        ${lcpGood}/${cwvData.length} pages good
                    </div>
                    <div class="cwv-metric-info">
                        <small>Good: ≤2.5s | Needs improvement: ≤4.0s | Poor: >4.0s</small>
                    </div>
                </div>
                
                <div class="cwv-metric-card">
                    <div class="cwv-metric-header">
                        <h3><i class="fas fa-layer-group"></i> CLS</h3>
                        <span class="cwv-label">Cumulative Layout Shift</span>
                    </div>
                    <div class="cwv-metric-value">${avgCLS ? avgCLS.toFixed(3) : 'N/A'}</div>
                    <div class="cwv-metric-score ${getScoreClass ? getScoreClass(clsGood, cwvData.length) : 'unknown'}">
                        ${clsGood}/${cwvData.length} pages good
                    </div>
                    <div class="cwv-metric-info">
                        <small>Good: ≤0.1 | Needs improvement: ≤0.25 | Poor: >0.25</small>
                    </div>
                </div>
                
                <div class="cwv-metric-card">
                    <div class="cwv-metric-header">
                        <h3><i class="fas fa-mouse-pointer"></i> INP</h3>
                        <span class="cwv-label">Interaction to Next Paint</span>
                    </div>
                    <div class="cwv-metric-value">${avgINP ? avgINP.toFixed(0) + 'ms' : 'N/A'}</div>
                    <div class="cwv-metric-score ${getScoreClass(inpGood, cwvData.filter(p => p.inp).length)}">
                        ${inpGood}/${cwvData.filter(p => p.inp).length} pages good
                    </div>
                    <div class="cwv-metric-info">
                        <small>Good: ≤200ms | Needs improvement: ≤500ms | Poor: >500ms</small>
                    </div>
                </div>
                
                <div class="cwv-metric-card">
                    <div class="cwv-metric-header">
                        <h3><i class="fas fa-server"></i> TTFB</h3>
                        <span class="cwv-label">Time to First Byte</span>
                    </div>
                    <div class="cwv-metric-value">${avgTTFB ? avgTTFB.toFixed(2) + 's' : 'N/A'}</div>
                    <div class="cwv-metric-score">
                        Server response time
                    </div>
                    <div class="cwv-metric-info">
                        <small>Good: ≤0.8s | Needs improvement: ≤1.8s | Poor: >1.8s</small>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="table-container" style="margin-top: 30px;">
            <h3 style="margin-bottom: 20px;">Page-by-Page Core Web Vitals</h3>
            <table class="audit-table">
                <thead>
                    <tr>
                        <th>Page</th>
                        <th>LCP</th>
                        <th>CLS</th>
                        <th>INP</th>
                        <th>TTFB</th>
                        <th>FCP</th>
                        <th>Issues</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${cwvData.map((page, idx) => `
                        <tr>
                            <td>
                                <a href="${page.url}" target="_blank">${truncateUrl(page.url, 50)}</a><br>
                                <small>${escapeHtml(page.title || '').substring(0, 40)}</small>
                            </td>
                            <td>
                                <span class="badge ${page.lcp_score === 'good' ? 'badge-success' : page.lcp_score === 'needs-improvement' ? 'badge-warning' : page.lcp_score === 'poor' ? 'badge-danger' : 'badge-secondary'}">
                                    ${page.lcp ? page.lcp.toFixed(2) + 's' : 'N/A'}
                                </span>
                            </td>
                            <td>
                                <span class="badge ${page.cls_score === 'good' ? 'badge-success' : page.cls_score === 'needs-improvement' ? 'badge-warning' : page.cls_score === 'poor' ? 'badge-danger' : 'badge-secondary'}">
                                    ${page.cls !== undefined ? page.cls.toFixed(3) : 'N/A'}
                                </span>
                            </td>
                            <td>
                                <span class="badge ${page.inp_score === 'good' ? 'badge-success' : page.inp_score === 'needs-improvement' ? 'badge-warning' : page.inp_score === 'poor' ? 'badge-danger' : 'badge-secondary'}">
                                    ${page.inp ? page.inp.toFixed(0) + 'ms' : 'N/A'}
                                </span>
                            </td>
                            <td>
                                <span class="badge ${page.ttfb_score === 'good' ? 'badge-success' : page.ttfb_score === 'needs-improvement' ? 'badge-warning' : page.ttfb_score === 'poor' ? 'badge-danger' : 'badge-secondary'}">
                                    ${page.ttfb ? page.ttfb.toFixed(2) + 's' : 'N/A'}
                                </span>
                            </td>
                            <td>${page.fcp ? page.fcp.toFixed(2) + 's' : 'N/A'}</td>
                            <td>
                                ${(page.lcp_issues.length + page.cls_issues.length) > 0 ? 
                                    `<span class="badge badge-warning">${page.lcp_issues.length + page.cls_issues.length} issues</span>` : 
                                    '<span class="badge badge-success">No issues</span>'
                                }
                            </td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="showCWVDetails(${idx})">
                                    <i class="fas fa-info-circle"></i> Details
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
        container.innerHTML = html;
        
        // Store data for details modal
        window.cwvData = cwvData;
    } catch (error) {
        console.error('Error in displayCoreWebVitals:', error);
        const container = document.getElementById('coreWebVitalsContainer');
        if (container) {
            container.innerHTML = `
                <div class="info-message" style="padding: 40px; text-align: center;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #dc3545; margin-bottom: 20px;"></i>
                    <h3>Error Loading Data</h3>
                    <p>An error occurred: ${error.message || 'Unknown error'}</p>
                    <p style="margin-top: 10px; font-size: 12px; color: #6c757d;">Check console for details.</p>
                </div>
            `;
        }
    }
}

// Display Advanced Performance Metrics
function displayAdvancedPerformance(data) {
    // This will enhance the existing performance display
    // The data is in page.advanced_performance
    if (!data.pages) return;
    
    // Update performance overview with advanced metrics
    data.pages.forEach(page => {
        const advPerf = page.advanced_performance;
        if (advPerf) {
            // Add to existing performance display
        }
    });
}

// Security explanations and recommendations
const SECURITY_INFO = {
    'https': {
        simple: 'HTTPS encrypts the connection between your website and visitors, keeping data private and secure.',
        technical: 'HTTPS (HyperText Transfer Protocol Secure) uses TLS/SSL encryption to protect data in transit. It prevents eavesdropping, tampering, and man-in-the-middle attacks.',
        why_important: 'Google prioritizes HTTPS sites, and browsers show warnings for HTTP sites. Required for many modern web features.',
        how_to_fix: [
            'Get an SSL certificate from your hosting provider or use Let\'s Encrypt (free)',
            'Install the certificate on your web server',
            'Set up automatic HTTP to HTTPS redirects',
            'Update all internal links to use HTTPS',
            'Update your sitemap and canonical URLs to HTTPS'
        ],
        icon: 'fa-lock'
    },
    'mixed_content': {
        simple: 'Mixed content happens when an HTTPS page loads resources (images, scripts) over HTTP, which browsers block.',
        technical: 'Mixed content occurs when a secure HTTPS page loads insecure HTTP resources. Browsers block active mixed content (scripts) and warn about passive mixed content (images).',
        why_important: 'Mixed content weakens security, causes broken functionality, and triggers browser warnings that reduce user trust.',
        how_to_fix: [
            'Update all resource URLs (images, CSS, JS) to use HTTPS',
            'Use protocol-relative URLs (//example.com/resource) or relative paths',
            'Check CSS background images and inline styles',
            'Update third-party script URLs (analytics, widgets) to HTTPS',
            'Use a content security policy to prevent mixed content'
        ],
        icon: 'fa-exclamation-triangle'
    },
    'hsts': {
        simple: 'HSTS tells browsers to always use HTTPS when connecting to your site, even if someone types HTTP.',
        technical: 'HTTP Strict Transport Security (HSTS) is a security header that forces browsers to use HTTPS connections. It prevents protocol downgrade attacks and cookie hijacking.',
        why_important: 'Prevents attackers from forcing HTTP connections and protects against SSL stripping attacks.',
        how_to_fix: [
            'Add header: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload',
            'Set max-age to at least 31536000 (1 year)',
            'Include includeSubDomains to protect all subdomains',
            'Add preload directive and submit to HSTS preload list for maximum protection'
        ],
        icon: 'fa-shield-alt'
    },
    'x_frame_options': {
        simple: 'Prevents your website from being embedded in iframes on other sites, protecting against clickjacking attacks.',
        technical: 'X-Frame-Options header controls whether a page can be displayed in a frame. Clickjacking uses iframes to trick users into clicking hidden elements.',
        why_important: 'Protects against clickjacking attacks where malicious sites embed your content to trick users.',
        how_to_fix: [
            'Add header: X-Frame-Options: DENY (blocks all framing)',
            'Or use: X-Frame-Options: SAMEORIGIN (allows same origin only)',
            'Configure in your web server (Apache, Nginx) or application framework'
        ],
        icon: 'fa-window-restore'
    },
    'csp': {
        simple: 'Content Security Policy limits which resources your page can load, blocking many types of attacks.',
        technical: 'Content Security Policy (CSP) is a security header that specifies allowed sources for scripts, styles, images, and other resources. It helps prevent XSS attacks, data injection, and other code injection vulnerabilities.',
        why_important: 'One of the most effective defenses against XSS attacks and data injection vulnerabilities.',
        how_to_fix: [
            'Start with: Content-Security-Policy: default-src \'self\'',
            'Add specific directives for scripts, styles, images as needed',
            'Use report-uri to monitor violations before enforcing',
            'Gradually tighten the policy based on your site\'s needs',
            'Use CSP nonces or hashes for inline scripts/styles'
        ],
        icon: 'fa-code'
    },
    'x_content_type_options': {
        simple: 'Prevents browsers from guessing file types, which could lead to security issues.',
        technical: 'X-Content-Type-Options: nosniff prevents MIME type sniffing, where browsers ignore Content-Type headers and guess file types. This prevents certain types of attacks.',
        why_important: 'Prevents MIME-sniffing attacks where malicious files are served with incorrect Content-Type headers.',
        how_to_fix: [
            'Add header: X-Content-Type-Options: nosniff',
            'Ensure your server sends correct Content-Type headers for all resources'
        ],
        icon: 'fa-file-code'
    },
    'x_xss_protection': {
        simple: 'Enables the browser\'s built-in XSS filter (though modern browsers rely more on CSP).',
        technical: 'X-XSS-Protection header enables the browser\'s cross-site scripting filter. However, modern browsers rely more on Content Security Policy.',
        why_important: 'Provides an additional layer of XSS protection for older browsers.',
        how_to_fix: [
            'Add header: X-XSS-Protection: 1; mode=block',
            'Note: CSP is the primary XSS defense in modern browsers'
        ],
        icon: 'fa-ban'
    },
    'referrer_policy': {
        simple: 'Controls how much information about where visitors came from is sent to other sites.',
        technical: 'Referrer-Policy header controls how much referrer information (the URL of the previous page) is included in requests. This helps protect user privacy.',
        why_important: 'Protects user privacy by limiting referrer information shared with third-party sites.',
        how_to_fix: [
            'Add header: Referrer-Policy: strict-origin-when-cross-origin',
            'Or use: Referrer-Policy: no-referrer (most private)',
            'Choose policy based on your privacy requirements'
        ],
        icon: 'fa-user-secret'
    },
    'permissions_policy': {
        simple: 'Controls which browser features and APIs your site can use (like camera, geolocation, etc.).',
        technical: 'Permissions-Policy (formerly Feature-Policy) header controls access to browser features and APIs. It allows you to restrict or enable features like camera, microphone, geolocation, etc.',
        why_important: 'Prevents unauthorized access to sensitive browser features and improves user privacy.',
        how_to_fix: [
            'Add header: Permissions-Policy: geolocation=(), microphone=(), camera=()',
            'Configure based on what features your site actually needs',
            'Use () to deny, * to allow, or specific origins to allow only those origins'
        ],
        icon: 'fa-user-cog'
    }
};

// Display Security & Trust Analysis
function displaySecurityAnalysis(data) {
    const container = document.getElementById('securityAnalysisContainer');
    if (!container || !data.pages) {
        if (container) {
            container.innerHTML = `
                <div class="info-message" style="padding: 40px; text-align: center;">
                    <i class="fas fa-info-circle" style="font-size: 48px; color: #6c757d; margin-bottom: 20px;"></i>
                    <h3>No Data Available</h3>
                    <p>No page data available for security analysis.</p>
                </div>
            `;
        }
        return;
    }
    
    // Collect security data
    const securityData = [];
    let httpsPages = 0;
    let mixedContentPages = 0;
    let secureHeadersCount = 0;
    let totalIssues = 0;
    
    data.pages.forEach(page => {
        const security = page.security_analysis;
        if (security) {
            securityData.push({
                url: page.url,
                title: page.title,
                ...security
            });
            
            if (security.https_enforcement?.is_https) httpsPages++;
            if (security.mixed_content?.has_mixed_content) mixedContentPages++;
            secureHeadersCount += security.security_headers?.present_count || 0;
            totalIssues += security.issues?.length || 0;
        }
    });
    
    if (securityData.length === 0) {
        container.innerHTML = `
            <div class="info-message" style="padding: 40px; text-align: center;">
                <i class="fas fa-info-circle" style="font-size: 48px; color: #6c757d; margin-bottom: 20px;"></i>
                <h3>No Security Data</h3>
                <p>Security analysis data not available. Run a new crawl to generate security reports.</p>
            </div>
        `;
        return;
    }
    
    const totalPages = securityData.length;
    const avgHeaders = Math.round(secureHeadersCount / totalPages);
    const securityScore = Math.round((httpsPages / totalPages * 0.4 + (totalPages - mixedContentPages) / totalPages * 0.3 + avgHeaders / 7 * 0.3) * 100);
    
    let html = `
        <style>
            .security-overview-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                text-align: center;
            }
            .security-overview-card h2 {
                margin: 0 0 10px 0;
                font-size: 48px;
                font-weight: bold;
            }
            .security-overview-card p {
                margin: 0;
                opacity: 0.9;
                font-size: 18px;
            }
            .security-metric-card-enhanced {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .security-metric-card-enhanced:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .security-metric-header {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }
            .security-metric-icon-large {
                font-size: 32px;
                margin-right: 15px;
                width: 50px;
                text-align: center;
            }
            .security-status-good { color: #28a745; }
            .security-status-warning { color: #ffc107; }
            .security-status-danger { color: #dc3545; }
            .security-info-section {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
            }
            .security-info-toggle {
                background: #f8f9fa;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                cursor: pointer;
                color: #495057;
                font-size: 14px;
                margin-top: 10px;
            }
            .security-info-toggle:hover {
                background: #e9ecef;
            }
            .security-info-content {
                display: none;
                margin-top: 15px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
            }
            .security-info-content.active {
                display: block;
            }
            .security-info-content h5 {
                margin-top: 0;
                color: #495057;
            }
            .security-info-content p {
                color: #6c757d;
                line-height: 1.6;
            }
            .fix-list {
                list-style: none;
                padding: 0;
            }
            .fix-list li {
                padding: 8px 0 8px 25px;
                position: relative;
                color: #495057;
            }
            .fix-list li:before {
                content: "✓";
                position: absolute;
                left: 0;
                color: #28a745;
                font-weight: bold;
            }
            .security-header-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .security-header-item {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 12px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .security-header-item.present {
                border-color: #28a745;
                background: #f8fff9;
            }
            .security-header-item.missing {
                border-color: #dc3545;
                background: #fff8f8;
            }
        </style>
        
        <!-- Overall Security Score -->
        <div class="security-overview-card">
            <h2>${securityScore}</h2>
            <p>Overall Security Score</p>
            <small style="opacity: 0.8; font-size: 14px;">Based on HTTPS, mixed content, and security headers</small>
        </div>
        
        <!-- Key Security Metrics -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div class="security-metric-card-enhanced">
                <div class="security-metric-header">
                    <div class="security-metric-icon-large ${httpsPages === totalPages ? 'security-status-good' : 'security-status-danger'}">
                        <i class="fas ${SECURITY_INFO.https.icon}"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">HTTPS</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${httpsPages}/${totalPages}</div>
                        <small style="color: #6c757d;">${httpsPages === totalPages ? 'All pages secure' : (totalPages - httpsPages) + ' pages need HTTPS'}</small>
                    </div>
                </div>
                ${httpsPages < totalPages ? `
                <div class="security-info-section">
                    <button class="security-info-toggle" onclick="toggleSecurityInfo('https-info')">
                        <i class="fas fa-info-circle"></i> Learn More & How to Fix
                    </button>
                    <div id="https-info" class="security-info-content">
                        <h5>What is HTTPS?</h5>
                        <p><strong>Simple:</strong> ${SECURITY_INFO.https.simple}</p>
                        <p><strong>Technical:</strong> ${SECURITY_INFO.https.technical}</p>
                        <h5>Why is it important?</h5>
                        <p>${SECURITY_INFO.https.why_important}</p>
                        <h5>How to Fix:</h5>
                        <ul class="fix-list">
                            ${SECURITY_INFO.https.how_to_fix.map(fix => `<li>${fix}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                ` : '<p style="color: #28a745; margin: 10px 0 0 0;"><i class="fas fa-check-circle"></i> All pages are using HTTPS</p>'}
            </div>
            
            <div class="security-metric-card-enhanced">
                <div class="security-metric-header">
                    <div class="security-metric-icon-large ${mixedContentPages === 0 ? 'security-status-good' : 'security-status-danger'}">
                        <i class="fas ${SECURITY_INFO.mixed_content.icon}"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">Mixed Content</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${mixedContentPages}</div>
                        <small style="color: #6c757d;">${mixedContentPages === 0 ? 'No issues found' : mixedContentPages + ' pages with issues'}</small>
                    </div>
                </div>
                ${mixedContentPages > 0 ? `
                <div class="security-info-section">
                    <button class="security-info-toggle" onclick="toggleSecurityInfo('mixed-content-info')">
                        <i class="fas fa-info-circle"></i> Learn More & How to Fix
                    </button>
                    <div id="mixed-content-info" class="security-info-content">
                        <h5>What is Mixed Content?</h5>
                        <p><strong>Simple:</strong> ${SECURITY_INFO.mixed_content.simple}</p>
                        <p><strong>Technical:</strong> ${SECURITY_INFO.mixed_content.technical}</p>
                        <h5>Why is it important?</h5>
                        <p>${SECURITY_INFO.mixed_content.why_important}</p>
                        <h5>How to Fix:</h5>
                        <ul class="fix-list">
                            ${SECURITY_INFO.mixed_content.how_to_fix.map(fix => `<li>${fix}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                ` : '<p style="color: #28a745; margin: 10px 0 0 0;"><i class="fas fa-check-circle"></i> No mixed content detected</p>'}
            </div>
            
            <div class="security-metric-card-enhanced">
                <div class="security-metric-header">
                    <div class="security-metric-icon-large ${avgHeaders >= 5 ? 'security-status-good' : avgHeaders >= 3 ? 'security-status-warning' : 'security-status-danger'}">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">Security Headers</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${avgHeaders}/7</div>
                        <small style="color: #6c757d;">${avgHeaders >= 5 ? 'Good coverage' : avgHeaders >= 3 ? 'Needs improvement' : 'Critical: Add more headers'}</small>
                    </div>
                </div>
                <div class="security-info-section">
                    <button class="security-info-toggle" onclick="toggleSecurityInfo('headers-info')">
                        <i class="fas fa-info-circle"></i> View All Headers & How to Fix
                    </button>
                    <div id="headers-info" class="security-info-content">
                        <h5>Security Headers Overview</h5>
                        <p>Security headers provide additional layers of protection against common web vulnerabilities. Here's what each header does:</p>
                        <div class="security-header-grid">
                            ${getSecurityHeadersDisplay(securityData)}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="security-metric-card-enhanced">
                <div class="security-metric-header">
                    <div class="security-metric-icon-large">
                        <i class="fas fa-cookie-bite"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">Cookie Consent</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${securityData.filter(s => s.cookie_consent?.detected).length}</div>
                        <small style="color: #6c757d;">Pages with consent banners detected</small>
                    </div>
                </div>
                <p style="color: #6c757d; margin: 10px 0 0 0; font-size: 14px;">
                    ${securityData.filter(s => s.cookie_consent?.detected).length > 0 ? 
                        '<i class="fas fa-check-circle"></i> Cookie consent banners detected (good for GDPR compliance)' : 
                        '<i class="fas fa-info-circle"></i> No cookie consent banners detected. Consider adding one if you use cookies.'}
                </p>
            </div>
        </div>
        
        <div class="table-container" style="margin-top: 30px;">
            <h3 style="margin-bottom: 20px;">Security Analysis by Page</h3>
            <table class="audit-table">
                <thead>
                    <tr>
                        <th>Page</th>
                        <th>HTTPS</th>
                        <th>Mixed Content</th>
                        <th>Security Headers</th>
                        <th>Cookie Consent</th>
                        <th>Overall Score</th>
                        <th>Issues</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${securityData.map((page, index) => {
                        const httpsStatus = page.https_enforcement?.is_https ? 'Yes' : 'No';
                        const mixedContentCount = page.mixed_content?.count || 0;
                        const headersCount = page.security_headers?.present_count || 0;
                        const headersTotal = 7;
                        const cookieConsent = page.cookie_consent?.detected ? 'Yes' : 'No';
                        const overallScore = page.overall_security_score || 'unknown';
                        const issuesCount = page.issues?.length || 0;
                        
                        return `
                            <tr>
                                <td>
                                    <a href="${page.url}" target="_blank">${truncateUrl(page.url, 50)}</a><br>
                                    <small>${escapeHtml(page.title || '').substring(0, 40)}</small>
                                </td>
                                <td>
                                    <span class="badge ${page.https_enforcement?.is_https ? 'badge-success' : 'badge-danger'}">
                                        ${httpsStatus}
                                    </span>
                                </td>
                                <td>
                                    ${mixedContentCount > 0 ? 
                                        `<span class="badge badge-danger">${mixedContentCount} issues</span>` : 
                                        '<span class="badge badge-success">None</span>'
                                    }
                                </td>
                                <td>
                                    <span class="badge ${headersCount >= 5 ? 'badge-success' : headersCount >= 3 ? 'badge-warning' : 'badge-danger'}">
                                        ${headersCount}/${headersTotal}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge ${cookieConsent === 'Yes' ? 'badge-info' : 'badge-secondary'}">
                                        ${cookieConsent}
                                    </span>
                                </td>
                                <td>
                                    <span class="score-badge ${overallScore}">${overallScore}</span>
                                </td>
                                <td>
                                    ${issuesCount > 0 ? 
                                        `<span class="badge badge-warning">${issuesCount} issues</span>` : 
                                        '<span class="badge badge-success">None</span>'
                                    }
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="showSecurityDetails(${index})">
                                        <i class="fas fa-info-circle"></i> Details
                                    </button>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Store data for details modal
    window.securityData = securityData;
}

// Indexability explanations and recommendations
const INDEXABILITY_INFO = {
    'robots_txt': {
        simple: 'Robots.txt is a file that tells search engines which pages they can and cannot crawl on your site.',
        technical: 'The robots.txt file uses the Robots Exclusion Protocol to control crawler access. Search engines check this file before crawling pages.',
        why_important: 'Blocks pages from being indexed. If important pages are blocked, they won\'t appear in search results.',
        how_to_fix: [
            'Check your robots.txt file at yoursite.com/robots.txt',
            'Look for "Disallow:" rules that block your page',
            'Remove or modify blocking rules for pages you want indexed',
            'Use "Allow:" to override "Disallow:" for specific paths',
            'Test your robots.txt with Google Search Console'
        ],
        icon: 'fa-robot'
    },
    'meta_robots': {
        simple: 'Meta robots tags in the HTML tell search engines whether to index a page or follow its links.',
        technical: 'The meta robots tag with "noindex" prevents a page from being added to search engine indexes. "nofollow" tells crawlers not to follow links.',
        why_important: 'Overrides robots.txt. A noindex tag means the page won\'t appear in search results, even if robots.txt allows it.',
        how_to_fix: [
            'Remove the meta robots tag if you want the page indexed',
            'Or change content from "noindex" to "index, follow"',
            'Check your CMS or template files for meta robots tags',
            'Use Google Search Console to request indexing after fixing'
        ],
        icon: 'fa-code'
    },
    'x_robots_tag': {
        simple: 'X-Robots-Tag is an HTTP header that does the same thing as meta robots tags but works for non-HTML files.',
        technical: 'X-Robots-Tag HTTP header provides indexing directives for all file types, not just HTML. It\'s processed by search engines before page content.',
        why_important: 'Can block indexing of PDFs, images, and other file types. Takes precedence over robots.txt for the files it covers.',
        how_to_fix: [
            'Check your server configuration or application code',
            'Remove or modify X-Robots-Tag headers that include "noindex"',
            'For Apache: Check .htaccess or httpd.conf',
            'For Nginx: Check nginx.conf',
            'For applications: Check middleware or framework settings'
        ],
        icon: 'fa-server'
    },
    'canonical': {
        simple: 'A canonical tag tells search engines which version of a page is the "main" one when you have duplicate or similar content.',
        technical: 'The rel="canonical" link element signals the preferred URL for duplicate content. It consolidates ranking signals to the canonical URL.',
        why_important: 'Prevents duplicate content issues and ensures the right page gets indexed. Missing or incorrect canonicals can split ranking signals.',
        how_to_fix: [
            'Add canonical tag: <link rel="canonical" href="https://yoursite.com/page">',
            'Use absolute URLs (including https://)',
            'Point to the preferred version of the page',
            'Ensure canonical points to an accessible, indexable page',
            'Avoid canonical chains (A→B→C, use A→A instead)'
        ],
        icon: 'fa-link'
    },
    'noindex_conflict': {
        simple: 'If a page has noindex but other pages link to it, you\'re wasting link equity on a page that won\'t rank.',
        technical: 'When a noindex page receives internal links, link equity is wasted since the page won\'t appear in search results. This reduces overall SEO value.',
        why_important: 'Either make the page indexable to benefit from links, or remove links if the page should remain private.',
        how_to_fix: [
            'Remove noindex if the page should be searchable',
            'Or remove internal links to noindex pages',
            'Redirect noindex pages to indexable equivalents',
            'Use noindex only for truly private pages (admin, cart, etc.)'
        ],
        icon: 'fa-exclamation-triangle'
    }
};

// Display Indexability Analysis
function displayIndexabilityAnalysis(data) {
    const container = document.getElementById('indexabilityAnalysisContainer');
    if (!container || !data.pages) {
        if (container) {
            container.innerHTML = `
                <div class="info-message" style="padding: 40px; text-align: center;">
                    <i class="fas fa-info-circle" style="font-size: 48px; color: #6c757d; margin-bottom: 20px;"></i>
                    <h3>No Data Available</h3>
                    <p>No page data available for indexability analysis.</p>
                </div>
            `;
        }
        return;
    }
    
    // Collect indexability data
    const indexabilityData = [];
    let indexableCount = 0;
    let noindexCount = 0;
    let blockedCount = 0;
    let canonicalIssues = 0;
    let noindexConflicts = 0;
    
    data.pages.forEach(page => {
        const indexability = page.indexability_analysis;
        if (indexability) {
            indexabilityData.push({
                url: page.url,
                title: page.title,
                ...indexability
            });
            
            if (indexability.indexability_status === 'indexable') indexableCount++;
            else if (indexability.indexability_status === 'noindex') noindexCount++;
            else if (indexability.indexability_status === 'blocked_by_robots_txt') blockedCount++;
            
            if (indexability.canonical && !indexability.canonical.is_self_canonical && indexability.canonical.present) {
                canonicalIssues++;
            }
            if (indexability.noindex_conflicts && indexability.noindex_conflicts.length > 0) {
                noindexConflicts++;
            }
        }
    });
    
    if (indexabilityData.length === 0) {
        container.innerHTML = `
            <div class="info-message" style="padding: 40px; text-align: center;">
                <i class="fas fa-info-circle" style="font-size: 48px; color: #6c757d; margin-bottom: 20px;"></i>
                <h3>No Indexability Data</h3>
                <p>Indexability analysis data not available. Run a new crawl to generate reports.</p>
            </div>
        `;
        return;
    }
    
    const totalPages = indexabilityData.length;
    const indexabilityScore = Math.round((indexableCount / totalPages * 0.6 + (totalPages - blockedCount) / totalPages * 0.4) * 100);
    
    let html = `
        <style>
            .indexability-overview-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                text-align: center;
            }
            .indexability-overview-card h2 {
                margin: 0 0 10px 0;
                font-size: 48px;
                font-weight: bold;
            }
            .indexability-metric-card-enhanced {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .indexability-metric-card-enhanced:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .indexability-info-section {
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
            }
            .indexability-info-toggle {
                background: #f8f9fa;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                cursor: pointer;
                color: #495057;
                font-size: 14px;
                margin-top: 10px;
            }
            .indexability-info-toggle:hover {
                background: #e9ecef;
            }
            .indexability-info-content {
                display: none;
                margin-top: 15px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
            }
            .indexability-info-content.active {
                display: block;
            }
        </style>
        
        <!-- Overall Indexability Score -->
        <div class="indexability-overview-card">
            <h2>${indexabilityScore}</h2>
            <p>Overall Indexability Score</p>
            <small style="opacity: 0.8; font-size: 14px;">Based on indexable pages and robots.txt blocking</small>
        </div>
        
        <!-- Key Indexability Metrics -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div class="indexability-metric-card-enhanced">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 32px; margin-right: 15px; width: 50px; text-align: center; color: #28a745;">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">Indexable Pages</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${indexableCount}/${totalPages}</div>
                        <small style="color: #6c757d;">${Math.round((indexableCount / totalPages) * 100)}% of pages</small>
                    </div>
                </div>
                <p style="color: #28a745; margin: 10px 0 0 0; font-size: 14px;">
                    <i class="fas fa-check-circle"></i> These pages can appear in search results
                </p>
            </div>
            
            <div class="indexability-metric-card-enhanced">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 32px; margin-right: 15px; width: 50px; text-align: center; color: #ffc107;">
                        <i class="fas fa-ban"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">Noindex Pages</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${noindexCount}</div>
                        <small style="color: #6c757d;">Blocked by meta robots or X-Robots-Tag</small>
                    </div>
                </div>
                ${noindexCount > 0 ? `
                <div class="indexability-info-section">
                    <button class="indexability-info-toggle" onclick="toggleIndexabilityInfo('noindex-info')">
                        <i class="fas fa-info-circle"></i> Learn More & How to Fix
                    </button>
                    <div id="noindex-info" class="indexability-info-content">
                        <h5>What is Noindex?</h5>
                        <p><strong>Simple:</strong> Noindex tells search engines not to show this page in search results.</p>
                        <p><strong>Technical:</strong> The noindex directive (via meta robots tag or X-Robots-Tag header) prevents a page from being added to search engine indexes, even if it's crawled.</p>
                        <h5>Why is it important?</h5>
                        <p>Use noindex for pages you don't want in search results (admin pages, cart pages, etc.). But if important pages are noindex, they won't rank.</p>
                        <h5>How to Fix (if needed):</h5>
                        <ul class="fix-list">
                            ${INDEXABILITY_INFO.meta_robots.how_to_fix.map(fix => `<li>${fix}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                ` : '<p style="color: #28a745; margin: 10px 0 0 0; font-size: 14px;"><i class="fas fa-check-circle"></i> No noindex pages detected</p>'}
            </div>
            
            <div class="indexability-metric-card-enhanced">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 32px; margin-right: 15px; width: 50px; text-align: center; color: #dc3545;">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">Blocked by robots.txt</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${blockedCount}</div>
                        <small style="color: #6c757d;">Pages blocked from crawling</small>
                    </div>
                </div>
                ${blockedCount > 0 ? `
                <div class="indexability-info-section">
                    <button class="indexability-info-toggle" onclick="toggleIndexabilityInfo('robots-txt-info')">
                        <i class="fas fa-info-circle"></i> Learn More & How to Fix
                    </button>
                    <div id="robots-txt-info" class="indexability-info-content">
                        <h5>What is robots.txt?</h5>
                        <p><strong>Simple:</strong> ${INDEXABILITY_INFO.robots_txt.simple}</p>
                        <p><strong>Technical:</strong> ${INDEXABILITY_INFO.robots_txt.technical}</p>
                        <h5>Why is it important?</h5>
                        <p>${INDEXABILITY_INFO.robots_txt.why_important}</p>
                        <h5>How to Fix:</h5>
                        <ul class="fix-list">
                            ${INDEXABILITY_INFO.robots_txt.how_to_fix.map(fix => `<li>${fix}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                ` : '<p style="color: #28a745; margin: 10px 0 0 0; font-size: 14px;"><i class="fas fa-check-circle"></i> No pages blocked by robots.txt</p>'}
            </div>
            
            <div class="indexability-metric-card-enhanced">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 32px; margin-right: 15px; width: 50px; text-align: center; color: ${canonicalIssues > 0 ? '#ffc107' : '#28a745'};">
                        <i class="fas ${INDEXABILITY_INFO.canonical.icon}"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">Canonical Issues</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${canonicalIssues}</div>
                        <small style="color: #6c757d;">Pages with non-self canonicals</small>
                    </div>
                </div>
                ${canonicalIssues > 0 ? `
                <div class="indexability-info-section">
                    <button class="indexability-info-toggle" onclick="toggleIndexabilityInfo('canonical-info')">
                        <i class="fas fa-info-circle"></i> Learn More & How to Fix
                    </button>
                    <div id="canonical-info" class="indexability-info-content">
                        <h5>What is a Canonical Tag?</h5>
                        <p><strong>Simple:</strong> ${INDEXABILITY_INFO.canonical.simple}</p>
                        <p><strong>Technical:</strong> ${INDEXABILITY_INFO.canonical.technical}</p>
                        <h5>Why is it important?</h5>
                        <p>${INDEXABILITY_INFO.canonical.why_important}</p>
                        <h5>How to Fix:</h5>
                        <ul class="fix-list">
                            ${INDEXABILITY_INFO.canonical.how_to_fix.map(fix => `<li>${fix}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                ` : '<p style="color: #28a745; margin: 10px 0 0 0; font-size: 14px;"><i class="fas fa-check-circle"></i> No canonical issues detected</p>'}
            </div>
            
            ${noindexConflicts > 0 ? `
            <div class="indexability-metric-card-enhanced" style="border-left: 4px solid #ffc107;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 32px; margin-right: 15px; width: 50px; text-align: center; color: #ffc107;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #212529;">Noindex Conflicts</h4>
                        <div style="font-size: 24px; font-weight: bold; color: #495057;">${noindexConflicts}</div>
                        <small style="color: #6c757d;">Noindex pages with internal links</small>
                    </div>
                </div>
                <div class="indexability-info-section">
                    <button class="indexability-info-toggle" onclick="toggleIndexabilityInfo('conflict-info')">
                        <i class="fas fa-info-circle"></i> Learn More & How to Fix
                    </button>
                    <div id="conflict-info" class="indexability-info-content">
                        <h5>What is a Noindex Conflict?</h5>
                        <p><strong>Simple:</strong> ${INDEXABILITY_INFO.noindex_conflict.simple}</p>
                        <p><strong>Technical:</strong> ${INDEXABILITY_INFO.noindex_conflict.technical}</p>
                        <h5>Why is it important?</h5>
                        <p>${INDEXABILITY_INFO.noindex_conflict.why_important}</p>
                        <h5>How to Fix:</h5>
                        <ul class="fix-list">
                            ${INDEXABILITY_INFO.noindex_conflict.how_to_fix.map(fix => `<li>${fix}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
            ` : ''}
        </div>
        
        <div class="table-container" style="margin-top: 30px;">
            <h3 style="margin-bottom: 20px;">Indexability Analysis by Page</h3>
            <table class="audit-table">
                <thead>
                    <tr>
                        <th>Page</th>
                        <th>Indexability Status</th>
                        <th>Crawlability Status</th>
                        <th>Robots.txt</th>
                        <th>Meta Robots</th>
                        <th>X-Robots-Tag</th>
                        <th>Canonical</th>
                        <th>Issues</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${indexabilityData.map((page, index) => {
                        const indexabilityStatus = page.indexability_status || 'unknown';
                        const crawlabilityStatus = page.crawlability_status || 'unknown';
                        const robotsTxt = page.robots_txt?.blocks_page ? 'Blocked' : 'Allowed';
                        const metaRobots = page.meta_robots?.noindex ? 'Noindex' : (page.meta_robots?.nofollow ? 'Nofollow' : 'None');
                        const xRobots = page.x_robots_tag?.present ? (page.x_robots_tag.noindex ? 'Noindex' : 'Present') : 'None';
                        const canonical = page.canonical?.present ? (page.canonical.is_self_canonical ? 'Self' : 'Other') : 'Missing';
                        const issuesCount = page.issues?.length || 0;
                        
                        return `
                            <tr>
                                <td>
                                    <a href="${page.url}" target="_blank">${truncateUrl(page.url, 50)}</a><br>
                                    <small>${escapeHtml(page.title || '').substring(0, 40)}</small>
                                </td>
                                <td>
                                    <span class="badge ${indexabilityStatus === 'indexable' ? 'badge-success' : indexabilityStatus === 'noindex' ? 'badge-warning' : 'badge-danger'}">
                                        ${indexabilityStatus.replace('_', ' ')}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge ${crawlabilityStatus === 'crawlable' ? 'badge-success' : 'badge-warning'}">
                                        ${crawlabilityStatus.replace('_', ' ')}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge ${page.robots_txt?.blocks_page ? 'badge-danger' : 'badge-success'}">
                                        ${robotsTxt}
                                    </span>
                                </td>
                                <td>${metaRobots}</td>
                                <td>${xRobots}</td>
                                <td>
                                    <span class="badge ${canonical === 'Self' ? 'badge-success' : canonical === 'Missing' ? 'badge-warning' : 'badge-info'}">
                                        ${canonical}
                                    </span>
                                </td>
                                <td>
                                    ${issuesCount > 0 ? 
                                        `<span class="badge badge-warning">${issuesCount} issues</span>` : 
                                        '<span class="badge badge-success">None</span>'
                                    }
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-primary" onclick="showIndexabilityDetails(${index})">
                                        <i class="fas fa-info-circle"></i> Details
                                    </button>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Store data for details modal
    window.indexabilityData = indexabilityData;
}

// Display Comprehensive SEO Scores
function displayComprehensiveSEOScores(data) {
    // Update the Advanced SEO Audit section with comprehensive scores
    if (!data.pages) return;
    
    // Check for comprehensive scores in site-wide analysis
    const siteAnalysis = data.advanced_site_analysis;
    if (siteAnalysis && siteAnalysis.comprehensive_site_score) {
        const siteScore = siteAnalysis.comprehensive_site_score;
        
        // Update site SEO score card
        const siteSeoScoreElement = document.getElementById('siteSeoScore');
        if (siteSeoScoreElement) {
            siteSeoScoreElement.textContent = Math.round(siteScore.overall_score || 0);
        }
    }
    
    // Enhance existing Advanced SEO display with comprehensive scores
    // This will be integrated into displayAdvancedSEO function
}

// Helper function to get security headers display
function getSecurityHeadersDisplay(securityData) {
    // Count how many pages have each header
    const headerCounts = {
        'Strict-Transport-Security': 0,
        'X-Content-Type-Options': 0,
        'X-Frame-Options': 0,
        'X-XSS-Protection': 0,
        'Content-Security-Policy': 0,
        'Referrer-Policy': 0,
        'Permissions-Policy': 0
    };
    
    securityData.forEach(page => {
        const present = page.security_headers?.present || {};
        Object.keys(headerCounts).forEach(header => {
            if (present[header]) headerCounts[header]++;
        });
    });
    
    const totalPages = securityData.length;
    const headerInfo = {
        'Strict-Transport-Security': { key: 'hsts', name: 'HSTS' },
        'X-Content-Type-Options': { key: 'x_content_type_options', name: 'X-Content-Type-Options' },
        'X-Frame-Options': { key: 'x_frame_options', name: 'X-Frame-Options' },
        'X-XSS-Protection': { key: 'x_xss_protection', name: 'X-XSS-Protection' },
        'Content-Security-Policy': { key: 'csp', name: 'Content Security Policy (CSP)' },
        'Referrer-Policy': { key: 'referrer_policy', name: 'Referrer-Policy' },
        'Permissions-Policy': { key: 'permissions_policy', name: 'Permissions-Policy' }
    };
    
    return Object.keys(headerCounts).map(header => {
        const count = headerCounts[header];
        const present = count > 0;
        const percentage = Math.round((count / totalPages) * 100);
        const info = headerInfo[header];
        const infoKey = info.key;
        const infoData = SECURITY_INFO[infoKey] || { simple: 'Security header', technical: '', why_important: '', how_to_fix: [] };
        
        return `
            <div class="security-header-item ${present ? 'present' : 'missing'}" style="cursor: pointer;" onclick="toggleSecurityHeaderInfo('${infoKey}')">
                <div style="flex: 1;">
                    <strong>${info.name}</strong><br>
                    <small style="color: #6c757d;">${count}/${totalPages} pages (${percentage}%)</small>
                    ${infoData.simple ? `<div id="${infoKey}-info" style="display: none; margin-top: 10px; padding: 10px; background: white; border-radius: 3px; border: 1px solid #dee2e6;">
                        <p style="font-size: 12px; margin: 5px 0;"><strong>What it does:</strong> ${infoData.simple}</p>
                        ${infoData.how_to_fix && infoData.how_to_fix.length > 0 ? `
                            <p style="font-size: 12px; margin: 5px 0;"><strong>How to add:</strong></p>
                            <ul style="font-size: 11px; margin: 5px 0 0 20px;">
                                ${infoData.how_to_fix.slice(0, 2).map(fix => `<li>${fix}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>` : ''}
                </div>
                <div>
                    ${present ? '<span style="color: #28a745; font-size: 20px;"><i class="fas fa-check-circle"></i></span>' : '<span style="color: #dc3545; font-size: 20px;"><i class="fas fa-times-circle"></i></span>'}
                </div>
            </div>
        `;
    }).join('');
}

// Toggle security header info
function toggleSecurityHeaderInfo(headerKey) {
    const element = document.getElementById(headerKey + '-info');
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

// Helper functions
function getScoreClass(goodCount, totalCount) {
    if (!totalCount || totalCount === 0) return 'unknown';
    const percentage = (goodCount / totalCount) * 100;
    if (percentage >= 75) return 'good';
    if (percentage >= 50) return 'needs-improvement';
    return 'poor';
}

function truncateUrl(url, maxLength) {
    if (!url) return '';
    if (url.length <= maxLength) return escapeHtml(url);
    return escapeHtml(url.substring(0, maxLength - 3)) + '...';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Details modals (to be implemented)
function showCWVDetails(index) {
    // Show Core Web Vitals details modal
    console.log('Show CWV details for index:', index);
}

function showSecurityDetails(index) {
    // Show Security details modal
    if (!window.securityData || !window.securityData[index]) {
        alert('Security data not available for this page');
        return;
    }
    
    const page = window.securityData[index];
    const https = page.https_enforcement || {};
    const mixedContent = page.mixed_content || {};
    const headers = page.security_headers || {};
    const cookieConsent = page.cookie_consent || {};
    const issues = page.issues || [];
    
    let html = `
        <div style="padding: 20px;">
            <h3 style="margin-top: 0;"><i class="fas fa-shield-alt"></i> Security Details</h3>
            <p><strong>Page:</strong> <a href="${page.url}" target="_blank">${page.url}</a></p>
            <p><strong>Title:</strong> ${escapeHtml(page.title || 'N/A')}</p>
            
            <hr style="margin: 20px 0;">
            
            <h4><i class="fas fa-lock"></i> HTTPS Status</h4>
            <div style="padding: 15px; background: ${https.is_https ? '#f8fff9' : '#fff8f8'}; border-left: 4px solid ${https.is_https ? '#28a745' : '#dc3545'}; margin-bottom: 20px;">
                <p><strong>Status:</strong> ${https.is_https ? '<span style="color: #28a745;">✓ HTTPS Enabled</span>' : '<span style="color: #dc3545;">✗ HTTP Only</span>'}</p>
                ${https.issue ? `<p><strong>Issue:</strong> ${https.issue}</p>` : ''}
                ${https.recommendation ? `<p><strong>Recommendation:</strong> ${https.recommendation}</p>` : ''}
                ${!https.is_https ? `
                    <div style="margin-top: 15px; padding: 10px; background: #e7f3ff; border-radius: 5px;">
                        <strong>How to Fix:</strong>
                        <ul style="margin: 10px 0 0 20px;">
                            ${SECURITY_INFO.https.how_to_fix.map(fix => `<li>${fix}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
            
            <h4><i class="fas fa-exclamation-triangle"></i> Mixed Content</h4>
            <div style="padding: 15px; background: ${mixedContent.has_mixed_content ? '#fff8f8' : '#f8fff9'}; border-left: 4px solid ${mixedContent.has_mixed_content ? '#dc3545' : '#28a745'}; margin-bottom: 20px;">
                <p><strong>Status:</strong> ${mixedContent.has_mixed_content ? `<span style="color: #dc3545;">✗ ${mixedContent.count} HTTP resources found</span>` : '<span style="color: #28a745;">✓ No mixed content</span>'}</p>
                ${mixedContent.http_resources && mixedContent.http_resources.length > 0 ? `
                    <p><strong>HTTP Resources Found:</strong></p>
                    <ul style="max-height: 200px; overflow-y: auto; background: white; padding: 10px; border-radius: 5px;">
                        ${mixedContent.http_resources.map(res => `<li><code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">${escapeHtml(res.url)}</code> <span style="color: #6c757d;">(${res.type})</span></li>`).join('')}
                    </ul>
                ` : ''}
                ${mixedContent.recommendation ? `<p style="margin-top: 10px;"><strong>Recommendation:</strong> ${mixedContent.recommendation}</p>` : ''}
                ${mixedContent.has_mixed_content ? `
                    <div style="margin-top: 15px; padding: 10px; background: #e7f3ff; border-radius: 5px;">
                        <strong>How to Fix:</strong>
                        <ul style="margin: 10px 0 0 20px;">
                            ${SECURITY_INFO.mixed_content.how_to_fix.map(fix => `<li>${fix}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
            
            <h4><i class="fas fa-shield-alt"></i> Security Headers (${headers.present_count || 0}/7)</h4>
            <div style="padding: 15px; background: #f8f9fa; border-left: 4px solid ${(headers.present_count || 0) >= 5 ? '#28a745' : (headers.present_count || 0) >= 3 ? '#ffc107' : '#dc3545'}; margin-bottom: 20px;">
                ${headers.present && Object.keys(headers.present).length > 0 ? `
                    <p><strong>Present Headers:</strong></p>
                    <ul style="background: white; padding: 10px; border-radius: 5px;">
                        ${Object.entries(headers.present).map(([name, value]) => `
                            <li style="margin-bottom: 10px;">
                                <strong>${name}:</strong><br>
                                <code style="background: #f0f0f0; padding: 5px; border-radius: 3px; display: inline-block; margin-top: 5px; word-break: break-all;">${escapeHtml(String(value))}</code>
                            </li>
                        `).join('')}
                    </ul>
                ` : '<p>No security headers found</p>'}
                
                ${headers.missing && headers.missing.length > 0 ? `
                    <p style="margin-top: 15px;"><strong>Missing Headers:</strong></p>
                    <ul style="background: #fff8f8; padding: 10px; border-radius: 5px;">
                        ${headers.missing.map(name => {
                            const headerKey = name.toLowerCase().replace(/-/g, '_').replace('strict_transport_security', 'hsts');
                            const info = SECURITY_INFO[headerKey] || { simple: 'Missing security header', how_to_fix: [] };
                            return `
                                <li style="margin-bottom: 10px; color: #dc3545;">
                                    <strong>${name}</strong>
                                    ${info.how_to_fix && info.how_to_fix.length > 0 ? `
                                        <div style="margin-top: 5px; padding: 8px; background: #e7f3ff; border-radius: 3px;">
                                            <small><strong>How to add:</strong></small>
                                            <ul style="margin: 5px 0 0 20px; font-size: 12px;">
                                                ${info.how_to_fix.slice(0, 2).map(fix => `<li>${fix}</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}
                                </li>
                            `;
                        }).join('')}
                    </ul>
                ` : ''}
                
                ${headers.issues && headers.issues.length > 0 ? `
                    <p style="margin-top: 15px;"><strong>Header Issues:</strong></p>
                    <ul>
                        ${headers.issues.map(issue => `
                            <li style="margin-bottom: 10px; padding: 10px; background: #fffbf0; border-left: 3px solid #ffc107; border-radius: 3px;">
                                <strong>${issue.header}:</strong> ${issue.issue}<br>
                                <small style="color: #6c757d; margin-top: 5px; display: block;"><strong>Fix:</strong> ${issue.recommendation}</small>
                            </li>
                        `).join('')}
                    </ul>
                ` : ''}
            </div>
            
            <h4><i class="fas fa-cookie-bite"></i> Cookie Consent</h4>
            <div style="padding: 15px; background: #f8f9fa; border-left: 4px solid #17a2b8; margin-bottom: 20px;">
                <p><strong>Detected:</strong> ${cookieConsent.detected ? '<span style="color: #28a745;">Yes ✓</span>' : '<span>No</span>'}</p>
                ${cookieConsent.confidence ? `<p><strong>Confidence:</strong> ${cookieConsent.confidence}</p>` : ''}
                ${cookieConsent.patterns_found && cookieConsent.patterns_found.length > 0 ? `
                    <p><strong>Patterns Found:</strong> ${cookieConsent.patterns_found.join(', ')}</p>
                ` : ''}
            </div>
            
            ${issues.length > 0 ? `
                <h4><i class="fas fa-exclamation-circle"></i> All Security Issues (${issues.length})</h4>
                <div style="margin-bottom: 20px;">
                    ${issues.map((issue, idx) => `
                        <div style="padding: 15px; background: ${issue.severity === 'critical' ? '#fff8f8' : '#fffbf0'}; border-left: 4px solid ${issue.severity === 'critical' ? '#dc3545' : '#ffc107'}; margin-bottom: 15px; border-radius: 5px;">
                            <p style="margin: 0 0 10px 0;">
                                <strong>#${idx + 1}. ${issue.type || 'Issue'}</strong> 
                                <span class="badge ${issue.severity === 'critical' ? 'badge-danger' : 'badge-warning'}" style="margin-left: 10px;">${issue.severity || 'warning'}</span>
                            </p>
                            ${issue.issue ? `<p style="margin: 5px 0;">${issue.issue}</p>` : ''}
                            ${issue.recommendation ? `
                                <div style="margin-top: 10px; padding: 10px; background: #e7f3ff; border-radius: 3px;">
                                    <strong>How to Fix:</strong>
                                    <p style="margin: 5px 0 0 0;">${issue.recommendation}</p>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            ` : '<div style="padding: 20px; background: #f8fff9; border-left: 4px solid #28a745; border-radius: 5px;"><p style="margin: 0; color: #28a745;"><i class="fas fa-check-circle"></i> <strong>No security issues found! Your page is secure.</strong></p></div>'}
        </div>
    `;
    
    // Show in modal (using existing modal if available)
    const modal = document.getElementById('pageModal');
    const modalBody = document.getElementById('modalBody');
    const modalTitle = document.getElementById('modalTitle');
    
    if (modal && modalBody && modalTitle) {
        modalTitle.innerHTML = '<i class="fas fa-shield-alt"></i> Security Analysis';
        modalBody.innerHTML = html;
        modal.style.display = 'block';
    } else {
        // Fallback: alert with basic info
        alert(`Security Analysis for ${page.url}\nHTTPS: ${https.is_https ? 'Yes' : 'No'}\nMixed Content: ${mixedContent.has_mixed_content ? 'Yes' : 'No'}\nSecurity Headers: ${headers.present_count || 0}/7\nIssues: ${issues.length}`);
    }
}

// Toggle security info sections
function toggleSecurityInfo(id) {
    const element = document.getElementById(id);
    if (element) {
        element.classList.toggle('active');
    }
}

function showIndexabilityDetails(index) {
    // Show Indexability details modal
    console.log('Show Indexability details for index:', index);
}

