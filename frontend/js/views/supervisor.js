/**
 * Supervisor Dashboard & Project Review Views
 */
const SupervisorView = {
  async renderDashboard(container) {
    container.innerHTML = `
      <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
        <div>
          <h1>Supervisor Dashboard</h1>
          <p>Review student academic submissions, verify plagiarism analysis, and provide guidance.</p>
        </div>
        <button class="btn btn-secondary" onclick="SupervisorView.renderProjects(document.getElementById('main-content-view'))">
          <i data-lucide="folder-check"></i> View All Submissions
        </button>
      </div>

      <!-- KPI Metric Cards -->
      <div class="grid grid-4 gap-4" style="margin-bottom: 2rem;">
        <div class="stat-card">
          <div class="stat-icon primary"><i data-lucide="users"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-sup-students">-</div>
            <div class="stat-label">Assigned Students</div>
          </div>
        </div>
        <div class="stat-card stat-warning">
          <div class="stat-icon warning"><i data-lucide="clock"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-sup-pending">-</div>
            <div class="stat-label">Pending Reviews</div>
          </div>
        </div>
        <div class="stat-card stat-success">
          <div class="stat-icon success"><i data-lucide="check-circle-2"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-sup-approved">-</div>
            <div class="stat-label">Approved Projects</div>
          </div>
        </div>
        <div class="stat-card stat-danger">
          <div class="stat-icon danger"><i data-lucide="alert-circle"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-sup-revision">-</div>
            <div class="stat-label">Revision Required</div>
          </div>
        </div>
      </div>

      <!-- Recent Submissions Queue Table -->
      <div class="card" style="margin-bottom: 2rem;">
        <div class="card-header">
          <h3 class="card-title">Recent Submissions Awaiting Action</h3>
        </div>
        <div id="sup-recent-submissions-table">
          <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading submissions...</div>
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    try {
      const data = await API.get('/dashboard/supervisor');
      document.getElementById('kpi-sup-students').textContent = data.assigned_students;
      document.getElementById('kpi-sup-pending').textContent = data.pending_reviews;
      document.getElementById('kpi-sup-approved').textContent = data.approved_projects;
      document.getElementById('kpi-sup-revision').textContent = data.revision_required;

      const subTable = document.getElementById('sup-recent-submissions-table');
      if (!data.recent_submissions || data.recent_submissions.length === 0) {
        subTable.innerHTML = `
          <div class="empty-state" style="padding:2.5rem 1rem;">
            <i data-lucide="check-check" class="empty-state-icon" style="color:var(--success);"></i>
            <h4 class="empty-state-title">All Caught Up!</h4>
            <p>No pending student submissions waiting for review at this moment.</p>
          </div>
        `;
      } else {
        subTable.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Student & Project</th>
                  <th>Document Version</th>
                  <th>Submitted At</th>
                  <th>Plagiarism Score</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                ${data.recent_submissions.map(s => {
                  let pillClass = s.similarity_score < 20 ? 'badge-original' : (s.similarity_score < 40 ? 'badge-low' : (s.similarity_score < 60 ? 'badge-moderate' : 'badge-critical'));

                  return `
                    <tr>
                      <td>
                        <strong style="color:var(--text-main);">${s.project_title}</strong>
                        <div style="font-size:0.8rem; color:var(--text-muted);">Author: ${s.student_name}</div>
                      </td>
                      <td>
                        <div class="flex items-center gap-1">
                          <i data-lucide="file-text" style="width:16px; height:16px; color:var(--primary);"></i>
                          <span>${s.original_filename} (v${s.version})</span>
                        </div>
                      </td>
                      <td>${new Date(s.submitted_at).toLocaleDateString()}</td>
                      <td>
                        <span class="badge ${pillClass}" style="font-size:0.8rem;">
                          ${s.similarity_score !== null ? `${s.similarity_score}%` : 'N/A'}
                        </span>
                      </td>
                      <td>
                        <div class="flex items-center gap-2">
                          <button class="btn btn-primary btn-sm" onclick="SupervisorView.openReviewModal(${s.project_id}, ${s.id})">
                            <i data-lucide="check-square"></i> Review & Grade
                          </button>
                          ${s.report_id ? `
                            <button class="btn btn-secondary btn-sm" onclick="ReportView.open(${s.report_id})">
                              <i data-lucide="shield-search"></i> Report
                            </button>
                          ` : ''}
                          <a href="${CONFIG.API_BASE_URL}/submissions/${s.id}/download" class="btn btn-secondary btn-sm btn-icon" title="Download">
                            <i data-lucide="download"></i>
                          </a>
                        </div>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        `;
      }

      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Supervisor Dashboard Error', err.message);
    }
  },

  async renderStudents(container) {
    container.innerHTML = `
      <div style="margin-bottom: 2rem;">
        <h1>Assigned Students</h1>
        <p>List of students under your academic supervision.</p>
      </div>

      <div class="card" id="sup-students-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading students...</div>
      </div>
    `;

    try {
      const projects = await API.get('/projects');
      const containerEl = document.getElementById('sup-students-container');

      if (!projects || projects.length === 0) {
        containerEl.innerHTML = `
          <div class="empty-state">
            <i data-lucide="users" class="empty-state-icon"></i>
            <h4 class="empty-state-title">No Students Assigned Yet</h4>
            <p>Academic administrators will assign students to you based on departmental quotas.</p>
          </div>
        `;
      } else {
        containerEl.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Matriculation No.</th>
                  <th>Project Title</th>
                  <th>Department</th>
                  <th>Current Status</th>
                  <th>Latest Similarity</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${projects.map(p => {
                  let badgeClass = `badge-${p.status.toLowerCase().replace(/\s+/g, '-')}`;
                  let scoreHtml = p.latest_similarity_score !== null 
                    ? `<span style="font-weight:700; color:${p.latest_similarity_score < 20 ? 'var(--success)' : (p.latest_similarity_score < 40 ? 'var(--warning)' : 'var(--danger)')};">${p.latest_similarity_score}%</span>`
                    : '<span style="color:var(--text-light);">-</span>';

                  return `
                    <tr>
                      <td>
                        <strong>${p.student ? p.student.full_name : 'Unknown'}</strong>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${p.student ? p.student.email : ''}</div>
                      </td>
                      <td>${p.student ? (p.student.matric_number || 'N/A') : 'N/A'}</td>
                      <td><span style="font-weight:600; color:var(--text-main);">${p.title}</span></td>
                      <td>${p.department}</td>
                      <td><span class="badge ${badgeClass}">${p.status}</span></td>
                      <td>${scoreHtml}</td>
                      <td>
                        <button class="btn btn-secondary btn-sm" onclick="SupervisorView.openReviewModal(${p.id})">
                          <i data-lucide="edit-3"></i> Review
                        </button>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        `;
      }
      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Students Error', err.message);
    }
  },

  async renderProjects(container) {
    container.innerHTML = `
      <div style="margin-bottom: 2rem;">
        <h1>Project Reviews & Submissions</h1>
        <p>Review student submissions, inspect plagiarism percentages, and assign feedback.</p>
      </div>

      <div class="card filter-bar" style="margin-bottom:1.5rem;">
        <div class="search-input-wrap">
          <i data-lucide="search" class="search-icon"></i>
          <input type="text" id="sup-search-input" class="search-input" placeholder="Search project title or student..." oninput="SupervisorView.filterProjects()">
        </div>
        <div class="flex items-center gap-3">
          <select id="sup-status-filter" class="form-control" style="width:auto;" onchange="SupervisorView.filterProjects()">
            <option value="">All Statuses</option>
            <option value="Submitted">Submitted (Needs Action)</option>
            <option value="Under Review">Under Review</option>
            <option value="Revision Required">Revision Required</option>
            <option value="Approved">Approved</option>
            <option value="Draft">Draft</option>
          </select>
        </div>
      </div>

      <div class="card" id="sup-projects-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading projects...</div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
    this.filterProjects();
  },

  async filterProjects() {
    const searchVal = document.getElementById('sup-search-input')?.value || '';
    const statusVal = document.getElementById('sup-status-filter')?.value || '';
    const container = document.getElementById('sup-projects-container');

    try {
      const projects = await API.get('/projects', { search: searchVal, status: statusVal });
      if (!projects || projects.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <i data-lucide="folder-search" class="empty-state-icon"></i>
            <h4 class="empty-state-title">No Projects Found</h4>
            <p>No projects match the selected search or status criteria.</p>
          </div>
        `;
      } else {
        container.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Project Details</th>
                  <th>Student Author</th>
                  <th>Status</th>
                  <th>Submissions</th>
                  <th>Plagiarism Score</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                ${projects.map(p => {
                  let badgeClass = `badge-${p.status.toLowerCase().replace(/\s+/g, '-')}`;
                  let scoreHtml = p.latest_similarity_score !== null 
                    ? `<span style="font-weight:700; color:${p.latest_similarity_score < 20 ? 'var(--success)' : (p.latest_similarity_score < 40 ? 'var(--warning)' : 'var(--danger)')};">${p.latest_similarity_score}%</span>`
                    : '<span style="color:var(--text-light);">-</span>';

                  return `
                    <tr>
                      <td>
                        <strong style="color:var(--text-main); font-size:0.95rem;">${p.title}</strong>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${p.department} • Session: ${p.academic_session}</div>
                      </td>
                      <td>
                        <strong>${p.student ? p.student.full_name : 'Unknown'}</strong>
                        <div style="font-size:0.75rem; color:var(--text-light);">${p.student ? (p.student.matric_number || '') : ''}</div>
                      </td>
                      <td><span class="badge ${badgeClass}">${p.status}</span></td>
                      <td><strong>${p.submissions_count}</strong> files</td>
                      <td>${scoreHtml}</td>
                      <td>
                        <div class="flex items-center gap-2">
                          <button class="btn btn-primary btn-sm" onclick="SupervisorView.openReviewModal(${p.id})">
                            <i data-lucide="check-square"></i> Review & Action
                          </button>
                        </div>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        `;
      }
      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Projects Error', err.message);
    }
  },

  async renderReports(container) {
    container.innerHTML = `
      <div style="margin-bottom: 2rem;">
        <h1>Plagiarism Analysis Archive</h1>
        <p>Institutional similarity results across supervised student thesis submissions.</p>
      </div>

      <div class="card" id="sup-reports-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading reports...</div>
      </div>
    `;

    try {
      const reports = await API.get('/reports');
      const containerEl = document.getElementById('sup-reports-container');

      if (!reports || reports.length === 0) {
        containerEl.innerHTML = `
          <div class="empty-state">
            <i data-lucide="shield-check" class="empty-state-icon"></i>
            <h4 class="empty-state-title">No Reports on File</h4>
            <p>No document similarity reports generated yet.</p>
          </div>
        `;
      } else {
        containerEl.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Student & Project</th>
                  <th>Original File</th>
                  <th>Similarity %</th>
                  <th>Classification</th>
                  <th>Matched Sources</th>
                  <th>Review Decision</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                ${reports.map(r => {
                  let pillClass = r.similarity_score < 20 ? 'badge-original' : (r.similarity_score < 40 ? 'badge-low' : (r.similarity_score < 60 ? 'badge-moderate' : 'badge-critical'));

                  return `
                    <tr>
                      <td>
                        <strong style="color:var(--text-main);">${r.project_title}</strong>
                        <div style="font-size:0.8rem; color:var(--text-muted);">${r.student_name} (${r.student_matric || 'Student'})</div>
                      </td>
                      <td>${r.original_filename} (v${r.submission_version})</td>
                      <td>
                        <span style="font-size:1.1rem; font-weight:800; color:${r.similarity_score < 20 ? 'var(--success)' : (r.similarity_score < 40 ? 'var(--warning)' : 'var(--danger)')};">
                          ${r.similarity_score}%
                        </span>
                      </td>
                      <td><span class="badge ${pillClass}">${r.result}</span></td>
                      <td>${r.matched_documents_count}</td>
                      <td><span style="font-weight:600; color:var(--primary);">${r.review_status}</span></td>
                      <td>
                        <div class="flex items-center gap-2">
                          <button class="btn btn-primary btn-sm" onclick="ReportView.open(${r.id})">
                            <i data-lucide="eye"></i> Inspect
                          </button>
                          <a href="${CONFIG.API_BASE_URL}/reports/${r.id}/download" target="_blank" class="btn btn-secondary btn-sm btn-icon" title="Print">
                            <i data-lucide="printer"></i>
                          </a>
                        </div>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        `;
      }
      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Reports Error', err.message);
    }
  },

  async renderProfile(container) {
    const user = Auth.getUser();
    container.innerHTML = `
      <div style="margin-bottom: 2rem;">
        <h1>Supervisor Profile</h1>
        <p>Faculty details and academic specialization settings.</p>
      </div>

      <div class="grid grid-3 gap-6">
        <div class="card">
          <div style="text-align:center; padding:1.5rem 0;">
            <div class="user-avatar" style="width:72px; height:72px; font-size:1.8rem; margin:0 auto 1rem auto;">
              ${user.full_name.charAt(0)}
            </div>
            <h3 style="font-size:1.2rem; margin-bottom:0.25rem;">${user.full_name}</h3>
            <p style="font-size:0.85rem; color:var(--text-muted);">${user.email}</p>
            <div style="margin-top:1rem;">
              <span class="badge badge-submitted">FACULTY SUPERVISOR</span>
            </div>
          </div>
        </div>

        <div class="card" style="grid-column: span 2;">
          <h3 class="card-title" style="margin-bottom:1.5rem;">Faculty Details</h3>
          <form onsubmit="SupervisorView.saveProfile(event)">
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input type="text" id="sup-fullname" class="form-control" value="${user.full_name}" required>
            </div>
            <div class="grid grid-2 gap-4">
              <div class="form-group">
                <label class="form-label">Department</label>
                <input type="text" id="sup-department" class="form-control" value="${user.department || 'Computer Science'}" required>
              </div>
              <div class="form-group">
                <label class="form-label">Staff ID</label>
                <input type="text" id="sup-staffid" class="form-control" value="${user.supervisor_profile ? (user.supervisor_profile.staff_id || '') : ''}">
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Specialization / Research Interests</label>
              <input type="text" id="sup-spec" class="form-control" value="${user.supervisor_profile ? (user.supervisor_profile.specialization || '') : ''}" placeholder="e.g. Distributed Computing, NLP, Cybersecurity">
            </div>
            <button type="submit" class="btn btn-primary" style="margin-top:1rem;">
              <i data-lucide="save"></i> Update Profile
            </button>
          </form>
        </div>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
  },

  async saveProfile(e) {
    e.preventDefault();
    const user = Auth.getUser();
    const payload = {
      full_name: document.getElementById('sup-fullname').value,
      department: document.getElementById('sup-department').value,
      staff_id: document.getElementById('sup-staffid').value,
      specialization: document.getElementById('sup-spec').value
    };

    try {
      const updated = await API.put(`/users/${user.id}`, payload);
      localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(updated));
      Toast.success('Profile Saved', 'Faculty information updated.');
    } catch (err) {
      Toast.error('Update Failed', err.message);
    }
  },

  async openReviewModal(projectId) {
    let modal = document.getElementById('supervisor-review-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'supervisor-review-modal';
      modal.className = 'modal-backdrop';
      document.body.appendChild(modal);
    }

    try {
      const project = await API.get(`/projects/${projectId}`);
      const latestSub = project.submissions && project.submissions.length > 0 ? project.submissions[0] : null;

      modal.innerHTML = `
        <div class="modal-dialog modal-lg">
          <div class="modal-header">
            <h3 class="modal-title">Review Project: ${project.title}</h3>
            <button class="modal-close-btn" onclick="Modal.close('supervisor-review-modal')">&times;</button>
          </div>
          <form onsubmit="SupervisorView.handleReviewSubmit(event, ${project.id})">
            <div class="modal-body" style="background:#F8FAFC;">
              <div class="card" style="margin-bottom:1.25rem;">
                <div class="flex items-center justify-between">
                  <div>
                    <h4 style="color:var(--text-main); margin-bottom:0.25rem;">Author: ${project.student ? project.student.full_name : 'Unknown'}</h4>
                    <div style="font-size:0.8rem; color:var(--text-muted);">${project.department} • Session: ${project.academic_session}</div>
                  </div>
                  <div>
                    <span class="badge badge-${project.status.toLowerCase().replace(/\s+/g, '-')}">${project.status}</span>
                  </div>
                </div>
              </div>

              ${latestSub ? `
                <div class="card" style="margin-bottom:1.25rem; background:#FFFFFF;">
                  <div class="flex items-center justify-between">
                    <div>
                      <div style="font-size:0.8rem; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Latest Submitted File</div>
                      <div style="font-weight:700; font-size:1rem; color:var(--text-main); margin-top:0.2rem;">${latestSub.original_filename} (v${latestSub.version})</div>
                      <div style="font-size:0.75rem; color:var(--text-light);">Submitted: ${new Date(latestSub.submitted_at).toLocaleString()}</div>
                    </div>
                    <div class="flex items-center gap-2">
                      <a href="${CONFIG.API_BASE_URL}/submissions/${latestSub.id}/download" class="btn btn-secondary btn-sm">
                        <i data-lucide="download"></i> Download Document
                      </a>
                      <button type="button" class="btn btn-primary btn-sm" onclick="ReportView.openBySubmission(${latestSub.id})">
                        <i data-lucide="shield-check"></i> View Similarity Report (${latestSub.similarity_score || 0}%)
                      </button>
                    </div>
                  </div>
                </div>
              ` : `
                <div class="empty-state" style="padding:1.5rem 0.5rem;">
                  <p>No document has been uploaded for this project yet.</p>
                </div>
              `}

              <!-- Review Action Form Controls -->
              <div class="card" style="background:#FFFFFF;">
                <h4 class="card-title" style="margin-bottom:1rem;">Supervisory Decision & Action</h4>
                <div class="form-group">
                  <label class="form-label">Review Decision *</label>
                  <select id="review-action-select" class="form-control" required>
                    <option value="Approved">Approve Project (Passed Plagiarism & Quality Review)</option>
                    <option value="Revision Required">Request Revision (Needs Text / Content Revision)</option>
                    <option value="Rejected">Reject Submission</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Detailed Feedback & Correction Notes *</label>
                  <textarea id="review-feedback-text" class="form-control" rows="4" placeholder="Provide actionable comments, critique, or approval remarks for the student..." required></textarea>
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" onclick="Modal.close('supervisor-review-modal')">Cancel</button>
              <button type="submit" class="btn btn-primary">
                <i data-lucide="check"></i> Submit Review Decision
              </button>
            </div>
          </form>
        </div>
      `;

      Modal.open('supervisor-review-modal');
      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Review Error', err.message);
    }
  },

  async handleReviewSubmit(e, projectId) {
    e.preventDefault();
    const action = document.getElementById('review-action-select').value;
    const feedbackText = document.getElementById('review-feedback-text').value;

    try {
      await API.put(`/projects/${projectId}/review`, {
        action: action,
        feedback_text: feedbackText
      });

      Modal.close('supervisor-review-modal');
      Toast.success('Review Submitted', `Project updated with decision: ${action}`);
      SupervisorView.renderProjects(document.getElementById('main-content-view'));
    } catch (err) {
      Toast.error('Review Failed', err.message);
    }
  }
};
