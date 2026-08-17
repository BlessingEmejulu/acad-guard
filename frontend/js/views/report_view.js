/**
 * Interactive Plagiarism Report Viewer & Modal
 */
const ReportView = {
  async open(reportId) {
    try {
      const report = await API.get(`/reports/${reportId}`);
      this.renderReportModal(report);
    } catch (err) {
      Toast.error('Report Error', 'Unable to load similarity report: ' + err.message);
    }
  },

  async openBySubmission(submissionId) {
    try {
      const report = await API.get(`/submissions/${submissionId}/report`);
      this.renderReportModal(report);
    } catch (err) {
      Toast.error('Report Error', 'Unable to load similarity report: ' + err.message);
    }
  },

  renderReportModal(report) {
    let modal = document.getElementById('plagiarism-report-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'plagiarism-report-modal';
      modal.className = 'modal-backdrop';
      document.body.appendChild(modal);
    }

    // Determine classification styling
    let tagClass = 'tag-original';
    let circleColorClass = 'color-original';
    if (report.similarity_score >= 60) {
      tagClass = 'tag-critical';
      circleColorClass = 'color-critical';
    } else if (report.similarity_score >= 40) {
      tagClass = 'tag-moderate';
      circleColorClass = 'color-moderate';
    } else if (report.similarity_score >= 20) {
      tagClass = 'tag-low';
      circleColorClass = 'color-low';
    }

    // Calculate SVG circle stroke dashoffset (circumference = 2 * PI * 60 ~= 377)
    const circumference = 377;
    const offset = circumference - (report.similarity_score / 100) * circumference;

    // Matched documents list
    let matchesHtml = '';
    if (!report.matches || report.matches.length === 0) {
      matchesHtml = `
        <div class="empty-state" style="padding: 2rem 1rem;">
          <i data-lucide="check-circle-2" class="empty-state-icon" style="color:var(--success);"></i>
          <h4 class="empty-state-title">No Significant Matches Found</h4>
          <p>This document exhibits high originality when compared against previously submitted research in the academic repository.</p>
        </div>
      `;
    } else {
      matchesHtml = report.matches.map(m => {
        let pillClass = m.similarity_score >= 50 ? 'high' : (m.similarity_score >= 20 ? 'moderate' : 'low');
        
        let snippetsHtml = '';
        if (m.matched_snippets && m.matched_snippets.length > 0) {
          snippetsHtml = `
            <div class="snippet-box">
              <div style="font-size:0.75rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:0.4rem;">Overlapping Text Snippets (${m.matched_snippets.length}):</div>
              <ul class="snippet-list">
                ${m.matched_snippets.map(s => `<li class="snippet-item"><mark>"${s}"</mark></li>`).join('')}
              </ul>
            </div>
          `;
        }

        return `
          <div class="match-card">
            <div class="match-header">
              <div>
                <div class="match-title">${m.matched_project_title}</div>
                <div class="match-source-meta">Author: ${m.matched_student_name} • Session: ${m.matched_academic_session}</div>
              </div>
              <div class="match-score-pill ${pillClass}">
                ${m.similarity_score}% Match
              </div>
            </div>
            ${snippetsHtml}
          </div>
        `;
      }).join('');
    }

    // Modal Content
    modal.innerHTML = `
      <div class="modal-dialog modal-lg">
        <div class="modal-header">
          <div class="flex items-center gap-2">
            <i data-lucide="shield-alert" style="color:var(--primary);"></i>
            <h3 class="modal-title">Similarity & Plagiarism Report</h3>
          </div>
          <button class="modal-close-btn" onclick="Modal.close('plagiarism-report-modal')">&times;</button>
        </div>

        <div class="modal-body" style="background-color:#F8FAFC;">
          <!-- Hero Card with Circular Score Meter -->
          <div class="score-hero-card">
            <div class="score-info">
              <div class="score-badge-tag ${tagClass}">
                <i data-lucide="shield-check"></i> ${report.result}
              </div>
              <h2 class="report-project-title">${report.project_title}</h2>
              <div class="report-sub-meta">
                <span><i data-lucide="user"></i> ${report.student_name} (${report.student_matric || 'Student'})</span>
                <span><i data-lucide="building"></i> ${report.department}</span>
                <span><i data-lucide="file-text"></i> ${report.original_filename} (v${report.submission_version})</span>
              </div>
            </div>

            <div class="score-circle-wrapper">
              <svg class="score-svg" viewBox="0 0 140 140">
                <circle class="score-bg-circle" cx="70" cy="70" r="60"></circle>
                <circle id="report-progress-svg" class="score-progress-circle ${circleColorClass}" cx="70" cy="70" r="60" style="stroke-dashoffset: 377;"></circle>
              </svg>
              <div class="score-center-text">
                <div class="score-percent-val">${report.similarity_score}%</div>
                <div class="score-percent-label">Similarity</div>
              </div>
            </div>
          </div>

          <!-- Metadata Box Grid -->
          <div class="report-meta-grid">
            <div class="meta-box">
              <div class="meta-box-label">Matched Papers</div>
              <div class="meta-box-value">${report.matched_documents_count} Sources</div>
            </div>
            <div class="meta-box">
              <div class="meta-box-label">Word Count</div>
              <div class="meta-box-value">${report.total_words || 0} Words</div>
            </div>
            <div class="meta-box">
              <div class="meta-box-label">Analysis Duration</div>
              <div class="meta-box-value">${report.processing_time}s</div>
            </div>
            <div class="meta-box">
              <div class="meta-box-label">Review Status</div>
              <div class="meta-box-value" style="font-size:0.9rem; color:var(--primary);">${report.review_status}</div>
            </div>
          </div>

          <!-- Document Matching Section -->
          <div style="margin-bottom:1.5rem;">
            <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:1rem; color:var(--text-main);">
              Matched Academic Submissions in Institutional Database (${report.matches ? report.matches.length : 0})
            </h3>
            ${matchesHtml}
          </div>

          <!-- Document Preview Snippet -->
          ${report.extracted_text_preview ? `
            <div class="card" style="margin-top:1.5rem; background:#FFFFFF;">
              <h4 style="font-size:0.95rem; margin-bottom:0.5rem; color:var(--text-muted);">Extracted Document Text Preview</h4>
              <div style="font-size:0.85rem; color:#475569; background:#F1F5F9; padding:1rem; border-radius:var(--radius-md); font-family:'JetBrains Mono',monospace; max-height:160px; overflow-y:auto; white-space:pre-wrap;">${report.extracted_text_preview}</div>
            </div>
          ` : ''}
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" onclick="Modal.close('plagiarism-report-modal')">Close</button>
          <a href="${CONFIG.API_BASE_URL}/reports/${report.id}/download" target="_blank" class="btn btn-primary">
            <i data-lucide="printer"></i> Print / Export Report
          </a>
        </div>
      </div>
    `;

    Modal.open('plagiarism-report-modal');

    // Trigger Lucide icons
    if (window.lucide) window.lucide.createIcons();

    // Trigger stroke animation after open
    setTimeout(() => {
      const svgProgress = document.getElementById('report-progress-svg');
      if (svgProgress) {
        svgProgress.style.strokeDashoffset = offset;
      }
    }, 100);
  }
};
