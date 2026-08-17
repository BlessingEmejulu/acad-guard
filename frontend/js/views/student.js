/**
 * Student Dashboard & Project Management Views
 */
const StudentView = {
  async renderDashboard(container) {
    container.innerHTML = `
      <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
        <div>
          <h1>Student Dashboard</h1>
          <p>Track your academic research projects, document submissions, and similarity reports.</p>
        </div>
        <button class="btn btn-primary" onclick="StudentView.openCreateProjectModal()">
          <i data-lucide="plus-circle"></i> Create New Project
        </button>
      </div>

      <!-- KPI Metric Cards -->
      <div class="grid grid-4 gap-4" style="margin-bottom: 2rem;" id="student-kpi-grid">
        <div class="stat-card">
          <div class="stat-icon primary"><i data-lucide="folder-git-2"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-total-projects">-</div>
            <div class="stat-label">Total Projects</div>
          </div>
        </div>
        <div class="stat-card stat-info">
          <div class="stat-icon info"><i data-lucide="upload-cloud"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-submitted-projects">-</div>
            <div class="stat-label">Submitted / Under Review</div>
          </div>
        </div>
        <div class="stat-card stat-success">
          <div class="stat-icon success"><i data-lucide="check-circle"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-approved-projects">-</div>
            <div class="stat-label">Approved Projects</div>
          </div>
        </div>
        <div class="stat-card stat-warning">
          <div class="stat-icon warning"><i data-lucide="alert-triangle"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-revision-projects">-</div>
            <div class="stat-label">Revision Required</div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-3 gap-6">
        <!-- Projects Table Column (2 cols) -->
        <div style="grid-column: span 2;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">My Academic Projects</h3>
              <a onclick="Router.navigate('student/projects')" class="btn btn-secondary btn-sm">View All</a>
            </div>
            <div id="student-recent-projects-table">
              <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading projects...</div>
            </div>
          </div>
        </div>

        <!-- Feedback & Activity Column (1 col) -->
        <div>
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">Supervisor Feedback</h3>
            </div>
            <div id="student-recent-feedback-list">
              <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading feedback...</div>
            </div>
          </div>
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Fetch live dashboard data
    try {
      const data = await API.get('/dashboard/student');
      document.getElementById('kpi-total-projects').textContent = data.total_projects;
      document.getElementById('kpi-submitted-projects').textContent = data.submitted_projects;
      document.getElementById('kpi-approved-projects').textContent = data.approved_projects;
      document.getElementById('kpi-revision-projects').textContent = data.revision_required_projects;

      // Render Projects
      const projContainer = document.getElementById('student-recent-projects-table');
      if (!data.recent_projects || data.recent_projects.length === 0) {
        projContainer.innerHTML = `
          <div class="empty-state">
            <i data-lucide="folder-plus" class="empty-state-icon"></i>
            <h4 class="empty-state-title">No Projects Created Yet</h4>
            <p>Get started by creating your first academic project.</p>
            <button class="btn btn-primary btn-sm" style="margin-top:1rem;" onclick="StudentView.openCreateProjectModal()">Create Project</button>
          </div>
        `;
      } else {
        projContainer.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Supervisor</th>
                  <th>Plagiarism</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${data.recent_projects.map(p => {
                  let badgeClass = `badge-${p.status.toLowerCase().replace(/\s+/g, '-')}`;
                  let scoreHtml = p.latest_similarity_score !== null 
                    ? `<span style="font-weight:700; color:${p.latest_similarity_score < 20 ? 'var(--success)' : (p.latest_similarity_score < 40 ? 'var(--warning)' : 'var(--danger)')};">${p.latest_similarity_score}%</span>`
                    : '<span style="color:var(--text-light);">No report</span>';

                  return `
                    <tr>
                      <td>
                        <strong style="color:var(--text-main); cursor:pointer;" onclick="StudentView.renderProjectDetail(${p.id})">${p.title}</strong>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${p.department} • ${p.academic_session}</div>
                      </td>
                      <td><span class="badge ${badgeClass}">${p.status}</span></td>
                      <td>${p.supervisor_info ? p.supervisor_info.full_name : '<span style="color:var(--text-light);">Unassigned</span>'}</td>
                      <td>${scoreHtml}</td>
                      <td>
                        <button class="btn btn-secondary btn-sm" onclick="StudentView.renderProjectDetail(${p.id})">
                          <i data-lucide="eye"></i> View
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

      // Render Feedback List
      const fbContainer = document.getElementById('student-recent-feedback-list');
      if (!data.recent_feedback || data.recent_feedback.length === 0) {
        fbContainer.innerHTML = `
          <div class="empty-state" style="padding:2rem 1rem;">
            <i data-lucide="message-square" class="empty-state-icon"></i>
            <p>No feedback received yet from supervisors.</p>
          </div>
        `;
      } else {
        fbContainer.innerHTML = `
          <div class="timeline">
            ${data.recent_feedback.map(fb => `
              <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div style="font-size:0.8rem; font-weight:700; color:var(--text-main);">${fb.supervisor_name}</div>
                <div style="font-size:0.75rem; color:var(--text-light); margin-bottom:0.25rem;">Project: ${fb.project_title}</div>
                <div style="font-size:0.85rem; color:var(--text-muted); background:#F8FAFC; padding:0.6rem 0.8rem; border-radius:var(--radius-md); border-left:3px solid var(--primary);">${fb.feedback_text}</div>
              </div>
            `).join('')}
          </div>
        `;
      }

      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Dashboard Error', err.message);
    }
  },

  async renderProjects(container) {
    container.innerHTML = `
      <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
        <div>
          <h1>My Academic Projects</h1>
          <p>Manage, view revisions, and upload new documents for your registered research projects.</p>
        </div>
        <button class="btn btn-primary" onclick="StudentView.openCreateProjectModal()">
          <i data-lucide="plus-circle"></i> Create New Project
        </button>
      </div>

      <!-- Filter Controls -->
      <div class="card filter-bar" style="margin-bottom:1.5rem;">
        <div class="search-input-wrap">
          <i data-lucide="search" class="search-icon"></i>
          <input type="text" id="project-search-input" class="search-input" placeholder="Search projects by title..." oninput="StudentView.filterProjects()">
        </div>
        <div class="flex items-center gap-3">
          <select id="project-status-filter" class="form-control" style="width:auto;" onchange="StudentView.filterProjects()">
            <option value="">All Statuses</option>
            <option value="Draft">Draft</option>
            <option value="Submitted">Submitted</option>
            <option value="Under Review">Under Review</option>
            <option value="Approved">Approved</option>
            <option value="Revision Required">Revision Required</option>
          </select>
        </div>
      </div>

      <!-- Projects List -->
      <div class="card" id="student-projects-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading projects...</div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
    this.filterProjects();
  },

  async filterProjects() {
    const searchVal = document.getElementById('project-search-input')?.value || '';
    const statusVal = document.getElementById('project-status-filter')?.value || '';
    const container = document.getElementById('student-projects-container');

    try {
      const projects = await API.get('/projects', { search: searchVal, status: statusVal });
      if (!projects || projects.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <i data-lucide="folder-search" class="empty-state-icon"></i>
            <h4 class="empty-state-title">No Projects Found</h4>
            <p>Try adjusting your search query or filter settings.</p>
          </div>
        `;
      } else {
        container.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Project Details</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Supervisor</th>
                  <th>Submissions</th>
                  <th>Similarity</th>
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
                        <strong style="color:var(--text-main); font-size:0.95rem; cursor:pointer;" onclick="StudentView.renderProjectDetail(${p.id})">${p.title}</strong>
                        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">${p.department} • Session: ${p.academic_session}</div>
                      </td>
                      <td><span style="font-size:0.8rem; background:#F1F5F9; padding:0.2rem 0.5rem; border-radius:var(--radius-sm);">${p.category || 'General'}</span></td>
                      <td><span class="badge ${badgeClass}">${p.status}</span></td>
                      <td>${p.supervisor_info ? p.supervisor_info.full_name : '<span style="color:var(--text-light);">Unassigned</span>'}</td>
                      <td><strong>${p.submissions_count}</strong> versions</td>
                      <td>${scoreHtml}</td>
                      <td>
                        <div class="flex items-center gap-2">
                          <button class="btn btn-primary btn-sm" onclick="StudentView.renderProjectDetail(${p.id})">
                            <i data-lucide="folder-open"></i> Manage
                          </button>
                          <button class="btn btn-secondary btn-sm" onclick="StudentView.openSubmitDocumentModal(${p.id})">
                            <i data-lucide="upload"></i> Submit
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

  async renderProjectDetail(projectId) {
    const mainView = document.getElementById('main-content-view');
    mainView.innerHTML = `<div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading project details...</div>`;

    try {
      const project = await API.get(`/projects/${projectId}`);
      const feedbacks = await API.get(`/projects/${projectId}/feedback`);

      let badgeClass = `badge-${project.status.toLowerCase().replace(/\s+/g, '-')}`;

      mainView.innerHTML = `
        <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
          <div>
            <a onclick="Router.navigate('student/projects')" style="display:inline-flex; align-items:center; gap:0.4rem; font-size:0.85rem; margin-bottom:0.5rem; color:var(--primary); cursor:pointer;">
              <i data-lucide="arrow-left"></i> Back to Projects
            </a>
            <h1>${project.title}</h1>
            <div style="font-size:0.9rem; color:var(--text-muted); margin-top:0.25rem;">
              Department of ${project.department} • Academic Session: ${project.academic_session} • Category: ${project.category || 'General'}
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="badge ${badgeClass}" style="font-size:0.85rem; padding:0.4rem 0.85rem;">${project.status}</span>
            <button class="btn btn-primary" onclick="StudentView.openSubmitDocumentModal(${project.id})">
              <i data-lucide="upload-cloud"></i> Submit New Version
            </button>
          </div>
        </div>

        <div class="grid grid-3 gap-6" style="margin-bottom:2rem;">
          <!-- Left 2 Columns: Submissions & Description -->
          <div style="grid-column: span 2;">
            <!-- Description -->
            <div class="card" style="margin-bottom:1.5rem;">
              <h3 class="card-title" style="margin-bottom:0.75rem;">Project Abstract & Description</h3>
              <p style="color:var(--text-main); font-size:0.95rem; line-height:1.6;">${project.description || 'No description provided.'}</p>
            </div>

            <!-- Versioned Submissions Table -->
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">Document Submissions (${project.submissions.length})</h3>
                <button class="btn btn-secondary btn-sm" onclick="StudentView.openSubmitDocumentModal(${project.id})">
                  <i data-lucide="plus"></i> Upload Revision
                </button>
              </div>

              ${project.submissions.length === 0 ? `
                <div class="empty-state">
                  <i data-lucide="file-up" class="empty-state-icon"></i>
                  <h4 class="empty-state-title">No Documents Submitted Yet</h4>
                  <p>Upload your research paper or thesis to initiate automatic plagiarism checks.</p>
                  <button class="btn btn-primary btn-sm" style="margin-top:1rem;" onclick="StudentView.openSubmitDocumentModal(${project.id})">
                    Upload Document
                  </button>
                </div>
              ` : `
                <div class="table-responsive">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>Version</th>
                        <th>Document File</th>
                        <th>Submitted Date</th>
                        <th>Similarity Score</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${project.submissions.map(s => {
                        let scoreHtml = s.similarity_score !== null 
                          ? `<span style="font-weight:700; color:${s.similarity_score < 20 ? 'var(--success)' : (s.similarity_score < 40 ? 'var(--warning)' : 'var(--danger)')};">${s.similarity_score}% (${s.plagiarism_result})</span>`
                          : '<span style="color:var(--text-light);">Processing...</span>';

                        return `
                          <tr>
                            <td><strong>v${s.version}</strong></td>
                            <td>
                              <div class="flex items-center gap-2">
                                <i data-lucide="file-text" style="color:var(--primary); width:18px; height:18px;"></i>
                                <span style="font-weight:600;">${s.original_filename}</span>
                              </div>
                              <div style="font-size:0.75rem; color:var(--text-light);">${(s.file_size / 1024).toFixed(1)} KB • ${s.file_type.toUpperCase()}</div>
                            </td>
                            <td>${new Date(s.submitted_at).toLocaleDateString()}</td>
                            <td>${scoreHtml}</td>
                            <td>
                              <div class="flex items-center gap-2">
                                <button class="btn btn-secondary btn-sm" onclick="ReportView.openBySubmission(${s.id})">
                                  <i data-lucide="shield-search"></i> Similarity Report
                                </button>
                                <a href="${CONFIG.API_BASE_URL}/submissions/${s.id}/download" class="btn btn-secondary btn-sm btn-icon" title="Download Document">
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
              `}
            </div>
          </div>

          <!-- Right Column: Supervisor & Feedback -->
          <div>
            <!-- Assigned Supervisor Card -->
            <div class="card" style="margin-bottom:1.5rem;">
              <h3 class="card-title" style="margin-bottom:1rem;">Faculty Supervisor</h3>
              ${project.supervisor_info ? `
                <div class="flex items-center gap-3">
                  <div class="user-avatar" style="width:48px; height:48px; font-size:1.1rem;">
                    ${project.supervisor_info.full_name.charAt(0)}
                  </div>
                  <div>
                    <div style="font-weight:700; color:var(--text-main); font-size:0.95rem;">${project.supervisor_info.full_name}</div>
                    <div style="font-size:0.8rem; color:var(--text-muted);">${project.supervisor_info.email}</div>
                    <div style="font-size:0.75rem; color:var(--text-light);">${project.supervisor_info.staff_id || 'Faculty Staff'}</div>
                  </div>
                </div>
              ` : `
                <div style="color:var(--text-muted); font-size:0.9rem;">
                  No supervisor assigned yet. The academic administrator will allocate a supervisor shortly.
                </div>
              `}
            </div>

            <!-- Feedback Stream -->
            <div class="card">
              <h3 class="card-title" style="margin-bottom:1rem;">Supervisor Feedback History</h3>
              ${feedbacks.length === 0 ? `
                <div class="empty-state" style="padding:1.5rem 0.5rem;">
                  <i data-lucide="message-square" class="empty-state-icon"></i>
                  <p>No feedback recorded yet.</p>
                </div>
              ` : `
                <div class="timeline">
                  ${feedbacks.map(f => `
                    <div class="timeline-item">
                      <div class="timeline-dot"></div>
                      <div style="font-weight:700; font-size:0.85rem; color:var(--text-main);">${f.supervisor_name}</div>
                      <div style="font-size:0.7rem; color:var(--text-light); margin-bottom:0.25rem;">${new Date(f.created_at).toLocaleString()} • <span style="font-weight:600; color:var(--primary);">${f.status || 'Feedback'}</span></div>
                      <div style="font-size:0.85rem; color:var(--text-main); background:#F8FAFC; padding:0.6rem 0.8rem; border-radius:var(--radius-md);">${f.feedback_text}</div>
                    </div>
                  `).join('')}
                </div>
              `}
            </div>
          </div>
        </div>
      `;

      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Error', err.message);
    }
  },

  async renderReports(container) {
    container.innerHTML = `
      <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
        <div>
          <h1>Plagiarism & Similarity Reports</h1>
          <p>Inspect detailed academic similarity reports and matching phrases across your submitted papers.</p>
        </div>
      </div>

      <div class="card" id="student-reports-table-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading reports...</div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    try {
      const reports = await API.get('/reports');
      const containerEl = document.getElementById('student-reports-table-container');

      if (!reports || reports.length === 0) {
        containerEl.innerHTML = `
          <div class="empty-state">
            <i data-lucide="shield-check" class="empty-state-icon"></i>
            <h4 class="empty-state-title">No Reports Generated Yet</h4>
            <p>Submit your project documents to view automated similarity analysis.</p>
          </div>
        `;
      } else {
        containerEl.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Project & File</th>
                  <th>Similarity Score</th>
                  <th>Result Classification</th>
                  <th>Matched Sources</th>
                  <th>Processing Time</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${reports.map(r => {
                  let pillClass = r.similarity_score < 20 ? 'badge-original' : (r.similarity_score < 40 ? 'badge-low' : (r.similarity_score < 60 ? 'badge-moderate' : 'badge-critical'));
                  return `
                    <tr>
                      <td>
                        <strong style="color:var(--text-main); cursor:pointer;" onclick="ReportView.open(${r.id})">${r.project_title}</strong>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${r.original_filename} (v${r.submission_version}) • ${new Date(r.submission_date).toLocaleDateString()}</div>
                      </td>
                      <td>
                        <span style="font-size:1.1rem; font-weight:800; color:${r.similarity_score < 20 ? 'var(--success)' : (r.similarity_score < 40 ? 'var(--warning)' : 'var(--danger)')};">
                          ${r.similarity_score}%
                        </span>
                      </td>
                      <td><span class="badge ${pillClass}">${r.result}</span></td>
                      <td>${r.matched_documents_count} documents</td>
                      <td>${r.processing_time}s</td>
                      <td>
                        <div class="flex items-center gap-2">
                          <button class="btn btn-primary btn-sm" onclick="ReportView.open(${r.id})">
                            <i data-lucide="eye"></i> View Full Report
                          </button>
                          <a href="${CONFIG.API_BASE_URL}/reports/${r.id}/download" target="_blank" class="btn btn-secondary btn-sm btn-icon" title="Print/Export">
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
        <h1>Student Profile</h1>
        <p>Manage your student record and account information.</p>
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
              <span class="badge badge-approved">${user.role.toUpperCase()}</span>
            </div>
          </div>
        </div>

        <div class="card" style="grid-column: span 2;">
          <h3 class="card-title" style="margin-bottom:1.5rem;">Academic Details</h3>
          <form onsubmit="StudentView.saveProfile(event)">
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input type="text" id="profile-fullname" class="form-control" value="${user.full_name}" required>
            </div>
            <div class="grid grid-2 gap-4">
              <div class="form-group">
                <label class="form-label">Matriculation Number</label>
                <input type="text" id="profile-matric" class="form-control" value="${user.matric_number || ''}" placeholder="e.g. CSC/2022/1042">
              </div>
              <div class="form-group">
                <label class="form-label">Department</label>
                <input type="text" id="profile-department" class="form-control" value="${user.department || 'Computer Science'}" required>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Phone Number</label>
              <input type="text" id="profile-phone" class="form-control" value="${user.phone || ''}" placeholder="+234...">
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
      full_name: document.getElementById('profile-fullname').value,
      matric_number: document.getElementById('profile-matric').value,
      department: document.getElementById('profile-department').value,
      phone: document.getElementById('profile-phone').value
    };

    try {
      const updated = await API.put(`/users/${user.id}`, payload);
      localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(updated));
      Toast.success('Profile Updated', 'Your profile details have been saved.');
      Navbar.renderSidebar(updated.role, 'student/profile');
    } catch (err) {
      Toast.error('Update Failed', err.message);
    }
  },

  async openCreateProjectModal() {
    let modal = document.getElementById('create-project-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'create-project-modal';
      modal.className = 'modal-backdrop';
      document.body.appendChild(modal);
    }

    // Load available supervisors for dropdown
    let supervisors = [];
    try {
      supervisors = await API.get('/supervisors');
    } catch (_) {}

    const user = Auth.getUser();

    modal.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-header">
          <h3 class="modal-title">Create New Academic Project</h3>
          <button class="modal-close-btn" onclick="Modal.close('create-project-modal')">&times;</button>
        </div>
        <form onsubmit="StudentView.handleCreateProject(event)">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Project Title *</label>
              <input type="text" id="new-proj-title" class="form-control" placeholder="e.g. Deep Learning for Medical Diagnostics..." required>
            </div>
            <div class="form-group">
              <label class="form-label">Project Description & Abstract</label>
              <textarea id="new-proj-desc" class="form-control" placeholder="Provide background summary and key objectives..."></textarea>
            </div>
            <div class="grid grid-2 gap-3">
              <div class="form-group">
                <label class="form-label">Category</label>
                <select id="new-proj-category" class="form-control">
                  <option value="Artificial Intelligence">Artificial Intelligence</option>
                  <option value="Cybersecurity">Cybersecurity</option>
                  <option value="Software Engineering">Software Engineering</option>
                  <option value="Distributed Systems">Distributed Systems</option>
                  <option value="Data Analytics">Data Analytics</option>
                  <option value="Mobile & Web Engineering">Mobile & Web Engineering</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Academic Session</label>
                <input type="text" id="new-proj-session" class="form-control" value="2025/2026" required>
              </div>
            </div>
            <div class="grid grid-2 gap-3">
              <div class="form-group">
                <label class="form-label">Department</label>
                <input type="text" id="new-proj-dept" class="form-control" value="${user.department || 'Computer Science'}" required>
              </div>
              <div class="form-group">
                <label class="form-label">Faculty Supervisor (Optional)</label>
                <select id="new-proj-supervisor" class="form-control">
                  <option value="">-- Let Admin Assign --</option>
                  ${supervisors.map(s => `<option value="${s.id}">${s.full_name} (${s.department || 'Faculty'})</option>`).join('')}
                </select>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" onclick="Modal.close('create-project-modal')">Cancel</button>
            <button type="submit" class="btn btn-primary">Create Project</button>
          </div>
        </form>
      </div>
    `;

    Modal.open('create-project-modal');
  },

  async handleCreateProject(e) {
    e.preventDefault();
    const supVal = document.getElementById('new-proj-supervisor').value;
    const payload = {
      title: document.getElementById('new-proj-title').value,
      description: document.getElementById('new-proj-desc').value,
      category: document.getElementById('new-proj-category').value,
      academic_session: document.getElementById('new-proj-session').value,
      department: document.getElementById('new-proj-dept').value,
      supervisor_id: supVal ? parseInt(supVal) : null
    };

    try {
      const proj = await API.post('/projects', payload);
      Modal.close('create-project-modal');
      Toast.success('Project Created', `Project '${proj.title}' created successfully.`);
      StudentView.renderProjectDetail(proj.id);
    } catch (err) {
      Toast.error('Creation Failed', err.message);
    }
  },

  openSubmitDocumentModal(projectId) {
    let modal = document.getElementById('submit-document-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'submit-document-modal';
      modal.className = 'modal-backdrop';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-header">
          <h3 class="modal-title">Upload Project Document</h3>
          <button class="modal-close-btn" onclick="Modal.close('submit-document-modal')">&times;</button>
        </div>
        <form onsubmit="StudentView.handleSubmitDocument(event, ${projectId})">
          <div class="modal-body">
            <p style="font-size:0.875rem; color:var(--text-muted); margin-bottom:1rem;">
              Upload your thesis or project document (.pdf, .docx, .txt). The system will automatically extract content, compute similarity against the institutional corpus, and issue a plagiarism report.
            </p>

            <div class="upload-dropzone" id="dropzone" onclick="document.getElementById('file-upload-input').click()">
              <input type="file" id="file-upload-input" class="upload-file-input" accept=".pdf,.docx,.doc,.txt" onchange="StudentView.handleFileSelected(event)">
              <i data-lucide="cloud-upload" class="upload-icon"></i>
              <div class="upload-title">Choose a document or drag & drop here</div>
              <div class="upload-subtitle">Supported formats: PDF, DOCX, TXT (Max size 25MB)</div>
            </div>

            <div id="selected-file-display" style="display:none;" class="selected-file-preview">
              <div class="selected-file-info">
                <i data-lucide="file-check" style="color:var(--success); width:24px; height:24px;"></i>
                <div>
                  <div id="selected-file-name" style="font-weight:700; font-size:0.9rem; color:var(--text-main);"></div>
                  <div id="selected-file-size" style="font-size:0.75rem; color:var(--text-muted);"></div>
                </div>
              </div>
              <button type="button" class="btn btn-secondary btn-sm" onclick="StudentView.clearSelectedFile(event)">Remove</button>
            </div>

            <div id="upload-progress-container" style="display:none; margin-top:1rem;">
              <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:600; color:var(--primary);">
                <span>Analyzing & Checking Plagiarism...</span>
                <span id="upload-pct-label">0%</span>
              </div>
              <div class="upload-progress-bar">
                <div id="upload-progress-fill" class="upload-progress-fill"></div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" onclick="Modal.close('submit-document-modal')">Cancel</button>
            <button type="submit" id="submit-doc-btn" class="btn btn-primary" disabled>
              <i data-lucide="upload"></i> Upload & Run Plagiarism Check
            </button>
          </div>
        </form>
      </div>
    `;

    Modal.open('submit-document-modal');
    if (window.lucide) window.lucide.createIcons();

    // Drag-and-drop listener setup
    const dropzone = document.getElementById('dropzone');
    ['dragenter', 'dragover'].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });
    ['dragleave', 'drop'].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });
    dropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const fileInput = document.getElementById('file-upload-input');
        fileInput.files = e.dataTransfer.files;
        StudentView.handleFileSelected({ target: fileInput });
      }
    });
  },

  handleFileSelected(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Check format
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!CONFIG.ALLOWED_EXTENSIONS.includes(ext)) {
      Toast.error('Invalid Format', `Allowed formats: ${CONFIG.ALLOWED_EXTENSIONS.join(', ')}`);
      e.target.value = '';
      return;
    }

    // Check size
    if (file.size > CONFIG.FILE_MAX_SIZE_MB * 1024 * 1024) {
      Toast.error('File Too Large', `Maximum allowed size is ${CONFIG.FILE_MAX_SIZE_MB}MB.`);
      e.target.value = '';
      return;
    }

    document.getElementById('selected-file-name').textContent = file.name;
    document.getElementById('selected-file-size').textContent = `${(file.size / 1024).toFixed(1)} KB`;
    document.getElementById('selected-file-display').style.display = 'flex';
    document.getElementById('submit-doc-btn').disabled = false;
    if (window.lucide) window.lucide.createIcons();
  },

  clearSelectedFile(e) {
    e.stopPropagation();
    document.getElementById('file-upload-input').value = '';
    document.getElementById('selected-file-display').style.display = 'none';
    document.getElementById('submit-doc-btn').disabled = true;
  },

  async handleSubmitDocument(e, projectId) {
    e.preventDefault();
    const fileInput = document.getElementById('file-upload-input');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const submitBtn = document.getElementById('submit-doc-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<div class="spinner"></div> Uploading & Analyzing...`;

    const progressCont = document.getElementById('upload-progress-container');
    const progressFill = document.getElementById('upload-progress-fill');
    const pctLabel = document.getElementById('upload-pct-label');
    progressCont.style.display = 'block';

    // Simulate animated upload and NLP comparison progression
    let pct = 10;
    const progressTimer = setInterval(() => {
      if (pct < 90) {
        pct += 15;
        progressFill.style.width = pct + '%';
        pctLabel.textContent = pct + '%';
      }
    }, 200);

    try {
      const submission = await API.upload(`/projects/${projectId}/submissions`, formData);
      clearInterval(progressTimer);
      progressFill.style.width = '100%';
      pctLabel.textContent = '100%';

      Modal.close('submit-document-modal');
      Toast.success('Analysis Complete', `Document submitted! Similarity score: ${submission.similarity_score}% (${submission.plagiarism_result})`);
      
      // Refresh project detail view and open report
      await StudentView.renderProjectDetail(projectId);
      if (submission.report_id) {
        ReportView.open(submission.report_id);
      }
    } catch (err) {
      clearInterval(progressTimer);
      Toast.error('Submission Failed', err.message);
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i data-lucide="upload"></i> Upload & Run Plagiarism Check`;
      if (window.lucide) window.lucide.createIcons();
    }
  }
};
