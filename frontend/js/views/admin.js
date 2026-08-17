/**
 * Administrator Dashboard, User Management, Analytics & Institutional Settings
 */
const AdminView = {
  charts: {},

  async renderDashboard(container) {
    container.innerHTML = `
      <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
        <div>
          <h1>Institutional Admin Dashboard</h1>
          <p>Global oversight of academic submissions, similarity statistics, and user access controls.</p>
        </div>
        <div class="flex items-center gap-2">
          <button class="btn btn-secondary" onclick="AdminView.handleBulkRecheck()">
            <i data-lucide="refresh-cw"></i> Bulk Plagiarism Re-check
          </button>
          <button class="btn btn-primary" onclick="AdminView.openCreateUserModal()">
            <i data-lucide="user-plus"></i> Add New User
          </button>
        </div>
      </div>

      <!-- System KPI Cards -->
      <div class="grid grid-4 gap-4" style="margin-bottom: 2rem;">
        <div class="stat-card">
          <div class="stat-icon primary"><i data-lucide="users"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-admin-users">-</div>
            <div class="stat-label">Total Users (Students & Faculty)</div>
          </div>
        </div>
        <div class="stat-card stat-info">
          <div class="stat-icon info"><i data-lucide="folder-git-2"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-admin-projects">-</div>
            <div class="stat-label">Total Academic Projects</div>
          </div>
        </div>
        <div class="stat-card stat-success">
          <div class="stat-icon success"><i data-lucide="file-check"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-admin-submissions">-</div>
            <div class="stat-label">Document Submissions</div>
          </div>
        </div>
        <div class="stat-card stat-warning">
          <div class="stat-icon warning"><i data-lucide="pie-chart"></i></div>
          <div class="stat-details">
            <div class="stat-value" id="kpi-admin-avg-similarity">-</div>
            <div class="stat-label">Avg Institutional Similarity</div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-3 gap-6" style="margin-bottom: 2rem;">
        <!-- Status Distribution Chart (1 col) -->
        <div class="card">
          <h3 class="card-title" style="margin-bottom:1rem;">Project Status Breakdown</h3>
          <div style="position:relative; height:240px;">
            <canvas id="statusChart"></canvas>
          </div>
        </div>

        <!-- Similarity Ranges Chart (1 col) -->
        <div class="card">
          <h3 class="card-title" style="margin-bottom:1rem;">Similarity Score Distribution</h3>
          <div style="position:relative; height:240px;">
            <canvas id="similarityChart"></canvas>
          </div>
        </div>

        <!-- Departmental Submissions (1 col) -->
        <div class="card">
          <h3 class="card-title" style="margin-bottom:1rem;">Submissions by Department</h3>
          <div style="position:relative; height:240px;">
            <canvas id="deptChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Recent Audit Activities -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Recent System Activities & Audit Trail</h3>
          <a onclick="Router.navigate('admin/audit-logs')" class="btn btn-secondary btn-sm">View Full Audit Log</a>
        </div>
        <div id="admin-recent-audit-table">
          <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading activities...</div>
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    try {
      const data = await API.get('/dashboard/admin');
      document.getElementById('kpi-admin-users').textContent = `${data.total_users} (${data.total_students} students, ${data.total_supervisors} supervisors)`;
      document.getElementById('kpi-admin-projects').textContent = data.total_projects;
      document.getElementById('kpi-admin-submissions').textContent = data.total_submissions;
      document.getElementById('kpi-admin-avg-similarity').textContent = `${data.average_similarity}%`;

      // Destroy old charts if existing
      Object.values(this.charts).forEach(c => c && c.destroy && c.destroy());

      // 1. Status Chart
      if (window.Chart && document.getElementById('statusChart')) {
        const ctxStatus = document.getElementById('statusChart').getContext('2d');
        this.charts.status = new Chart(ctxStatus, {
          type: 'doughnut',
          data: {
            labels: Object.keys(data.status_distribution),
            datasets: [{
              data: Object.values(data.status_distribution),
              backgroundColor: ['#94A3B8', '#0EA5E9', '#F59E0B', '#22C55E', '#EF4444', '#EA580C', '#8B5CF6'],
              borderWidth: 2,
              borderColor: '#FFFFFF'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: 'Inter', size: 11 } } }
            }
          }
        });
      }

      // 2. Similarity Ranges Chart
      if (window.Chart && document.getElementById('similarityChart')) {
        const ctxSim = document.getElementById('similarityChart').getContext('2d');
        this.charts.sim = new Chart(ctxSim, {
          type: 'bar',
          data: {
            labels: Object.keys(data.similarity_distribution),
            datasets: [{
              label: 'Papers Count',
              data: Object.values(data.similarity_distribution),
              backgroundColor: ['#22C55E', '#0EA5E9', '#F59E0B', '#EF4444'],
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true, ticks: { stepSize: 1 } },
              x: { ticks: { font: { family: 'Inter', size: 10 } } }
            }
          }
        });
      }

      // 3. Dept Chart
      if (window.Chart && document.getElementById('deptChart')) {
        const ctxDept = document.getElementById('deptChart').getContext('2d');
        this.charts.dept = new Chart(ctxDept, {
          type: 'bar',
          data: {
            labels: data.submission_trends.map(t => t.department),
            datasets: [{
              label: 'Submissions',
              data: data.submission_trends.map(t => t.count),
              backgroundColor: '#2563EB',
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true, ticks: { stepSize: 1 } },
              x: { ticks: { font: { family: 'Inter', size: 10 } } }
            }
          }
        });
      }

      // Render Activities Table
      const auditTable = document.getElementById('admin-recent-audit-table');
      if (!data.recent_activities || data.recent_activities.length === 0) {
        auditTable.innerHTML = `<div class="empty-state"><p>No recent activity logs.</p></div>`;
      } else {
        auditTable.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Description</th>
                  <th>User</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                ${data.recent_activities.map(a => `
                  <tr>
                    <td><span class="badge badge-submitted">${a.action}</span></td>
                    <td>${a.description}</td>
                    <td><strong>${a.user_name}</strong></td>
                    <td>${new Date(a.created_at).toLocaleString()}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `;
      }

    } catch (err) {
      Toast.error('Admin Dashboard Error', err.message);
    }
  },

  async renderUsers(container) {
    container.innerHTML = `
      <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
        <div>
          <h1>User Management Directory</h1>
          <p>Create, update, search, and manage access credentials for students, supervisors, and administrators.</p>
        </div>
        <button class="btn btn-primary" onclick="AdminView.openCreateUserModal()">
          <i data-lucide="user-plus"></i> Create User
        </button>
      </div>

      <div class="card filter-bar" style="margin-bottom:1.5rem;">
        <div class="search-input-wrap">
          <i data-lucide="search" class="search-icon"></i>
          <input type="text" id="user-search-input" class="search-input" placeholder="Search by name, email, matric..." oninput="AdminView.filterUsers()">
        </div>
        <div class="flex items-center gap-3">
          <select id="user-role-filter" class="form-control" style="width:auto;" onchange="AdminView.filterUsers()">
            <option value="">All Roles</option>
            <option value="student">Students</option>
            <option value="supervisor">Supervisors</option>
            <option value="admin">Administrators</option>
          </select>
        </div>
      </div>

      <div class="card" id="admin-users-table-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading users...</div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
    this.filterUsers();
  },

  async filterUsers() {
    const searchVal = document.getElementById('user-search-input')?.value || '';
    const roleVal = document.getElementById('user-role-filter')?.value || '';
    const container = document.getElementById('admin-users-table-container');

    try {
      const users = await API.get('/users', { search: searchVal, role: roleVal });
      if (!users || users.length === 0) {
        container.innerHTML = `<div class="empty-state"><i data-lucide="users" class="empty-state-icon"></i><h4 class="empty-state-title">No Users Found</h4></div>`;
      } else {
        container.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>User Profile</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Identifier (Matric / Staff ID)</th>
                  <th>Status</th>
                  <th>Created Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                ${users.map(u => {
                  let roleBadge = u.role === 'admin' ? 'badge-critical' : (u.role === 'supervisor' ? 'badge-submitted' : 'badge-approved');
                  let ident = u.role === 'student' ? (u.matric_number || 'N/A') : (u.supervisor_profile ? (u.supervisor_profile.staff_id || 'Staff') : 'N/A');

                  return `
                    <tr>
                      <td>
                        <div class="flex items-center gap-3">
                          <div class="user-avatar" style="width:36px; height:36px; font-size:0.9rem;">${u.full_name.charAt(0)}</div>
                          <div>
                            <strong style="color:var(--text-main);">${u.full_name}</strong>
                            <div style="font-size:0.75rem; color:var(--text-muted);">${u.email}</div>
                          </div>
                        </div>
                      </td>
                      <td><span class="badge ${roleBadge}">${u.role.toUpperCase()}</span></td>
                      <td>${u.department || 'N/A'}</td>
                      <td><code>${ident}</code></td>
                      <td>
                        <span class="badge ${u.is_active ? 'badge-original' : 'badge-rejected'}">
                          ${u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>${new Date(u.created_at).toLocaleDateString()}</td>
                      <td>
                        <div class="flex items-center gap-2">
                          <button class="btn btn-secondary btn-sm" onclick="AdminView.openEditUserModal(${u.id})">
                            <i data-lucide="edit-2"></i> Edit
                          </button>
                          <button class="btn btn-danger btn-sm btn-icon" title="Delete User" onclick="AdminView.confirmDeleteUser(${u.id}, '${u.email}')">
                            <i data-lucide="trash-2"></i>
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
      Toast.error('Users Error', err.message);
    }
  },

  async renderSupervisors(container) {
    container.innerHTML = `
      <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
        <div>
          <h1>Supervisor Allocation & Student Capacity</h1>
          <p>Monitor faculty supervisor capacity and assign supervisors to unassigned student projects.</p>
        </div>
      </div>

      <div class="card" id="admin-supervisors-container" style="margin-bottom:2rem;">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading supervisor roster...</div>
      </div>

      <div class="card" id="admin-unassigned-projects-container">
        <div class="card-header">
          <h3 class="card-title">Projects Awaiting Supervisor Assignment</h3>
        </div>
        <div id="unassigned-table-body">
          <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Checking unassigned projects...</div>
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    try {
      const supervisors = await API.get('/supervisors');
      const allProjects = await API.get('/projects');

      // Render Supervisor Capacity Grid
      const supCont = document.getElementById('admin-supervisors-container');
      supCont.innerHTML = `
        <h3 class="card-title" style="margin-bottom:1.25rem;">Faculty Supervisors Roster (${supervisors.length})</h3>
        <div class="grid grid-3 gap-4">
          ${supervisors.map(s => `
            <div class="card" style="border-left:4px solid var(--primary); background:#F8FAFC;">
              <div class="flex items-center justify-between" style="margin-bottom:0.75rem;">
                <strong style="color:var(--text-main); font-size:1rem;">${s.full_name}</strong>
                <span class="badge badge-submitted">${s.department || 'Faculty'}</span>
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">${s.email} • Staff ID: ${s.staff_id || 'N/A'}</div>
              <div style="font-size:0.8rem; color:var(--text-main); margin-bottom:0.75rem;"><strong>Specialization:</strong> ${s.specialization || 'General Computing'}</div>
              <div class="flex items-center justify-between" style="font-size:0.85rem; font-weight:600;">
                <span>Active Supervised Students:</span>
                <span style="color:var(--primary); font-size:1.1rem;">${s.assigned_count} / ${s.max_students}</span>
              </div>
            </div>
          `).join('')}
        </div>
      `;

      // Filter unassigned projects
      const unassigned = allProjects.filter(p => !p.supervisor_id);
      const unassignedCont = document.getElementById('unassigned-table-body');
      if (unassigned.length === 0) {
        unassignedCont.innerHTML = `
          <div class="empty-state" style="padding:2rem 1rem;">
            <i data-lucide="check-circle-2" class="empty-state-icon" style="color:var(--success);"></i>
            <h4 class="empty-state-title">All Projects Assigned</h4>
            <p>Every active student project has an allocated faculty supervisor.</p>
          </div>
        `;
      } else {
        unassignedCont.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Project Title</th>
                  <th>Student</th>
                  <th>Department</th>
                  <th>Session</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                ${unassigned.map(p => `
                  <tr>
                    <td><strong>${p.title}</strong></td>
                    <td>${p.student ? p.student.full_name : 'Unknown'}</td>
                    <td>${p.department}</td>
                    <td>${p.academic_session}</td>
                    <td>
                      <button class="btn btn-primary btn-sm" onclick="AdminView.openAssignSupervisorModal(${p.id}, '${p.title.replace(/'/g, "\\'")}')">
                        <i data-lucide="user-plus"></i> Assign Supervisor
                      </button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `;
      }

      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Supervisors Error', err.message);
    }
  },

  async renderProjects(container) {
    container.innerHTML = `
      <div style="margin-bottom: 2rem;">
        <h1>All Academic Projects</h1>
        <p>Master institutional registry of registered research projects.</p>
      </div>

      <div class="card filter-bar" style="margin-bottom:1.5rem;">
        <div class="search-input-wrap">
          <i data-lucide="search" class="search-icon"></i>
          <input type="text" id="admin-proj-search" class="search-input" placeholder="Search project title or author..." oninput="AdminView.filterMasterProjects()">
        </div>
      </div>

      <div class="card" id="admin-master-projects-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading all projects...</div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();
    this.filterMasterProjects();
  },

  async filterMasterProjects() {
    const searchVal = document.getElementById('admin-proj-search')?.value || '';
    const container = document.getElementById('admin-master-projects-container');

    try {
      const projects = await API.get('/projects', { search: searchVal });
      if (!projects || projects.length === 0) {
        container.innerHTML = `<div class="empty-state"><p>No projects match your query.</p></div>`;
      } else {
        container.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Project Title</th>
                  <th>Student Author</th>
                  <th>Supervisor</th>
                  <th>Department</th>
                  <th>Status</th>
                  <th>Submissions</th>
                  <th>Latest Similarity</th>
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
                        <strong style="color:var(--text-main);">${p.title}</strong>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${p.category || 'General'} • ${p.academic_session}</div>
                      </td>
                      <td><strong>${p.student ? p.student.full_name : 'Unknown'}</strong></td>
                      <td>${p.supervisor_info ? p.supervisor_info.full_name : '<span style="color:var(--warning);">Unassigned</span>'}</td>
                      <td>${p.department}</td>
                      <td><span class="badge ${badgeClass}">${p.status}</span></td>
                      <td>${p.submissions_count} versions</td>
                      <td>${scoreHtml}</td>
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

  async renderSubmissions(container) {
    container.innerHTML = `
      <div style="margin-bottom: 2rem;">
        <h1>All Submissions Archive</h1>
        <p>Complete repository of uploaded documents across all student projects.</p>
      </div>

      <div class="card" id="admin-submissions-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading submissions...</div>
      </div>
    `;

    try {
      const projects = await API.get('/projects');
      const containerEl = document.getElementById('admin-submissions-container');

      // Fetch all submissions from all projects
      let allSubs = [];
      for (const p of projects) {
        const pDetails = await API.get(`/projects/${p.id}`);
        if (pDetails.submissions) {
          pDetails.submissions.forEach(s => {
            allSubs.push({ ...s, project_id: p.id, project_title: p.title, department: p.department, student_name: p.student ? p.student.full_name : 'Student' });
          });
        }
      }

      if (allSubs.length === 0) {
        containerEl.innerHTML = `<div class="empty-state"><p>No documents submitted in database yet.</p></div>`;
      } else {
        containerEl.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Document & Version</th>
                  <th>Project Title</th>
                  <th>Student Author</th>
                  <th>Submitted Date</th>
                  <th>Similarity Result</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                ${allSubs.map(s => {
                  let scoreHtml = s.similarity_score !== null 
                    ? `<span style="font-weight:700; color:${s.similarity_score < 20 ? 'var(--success)' : (s.similarity_score < 40 ? 'var(--warning)' : 'var(--danger)')};">${s.similarity_score}% (${s.plagiarism_result})</span>`
                    : 'Checked';

                  return `
                    <tr>
                      <td>
                        <div class="flex items-center gap-2">
                          <i data-lucide="file-text" style="color:var(--primary); width:18px; height:18px;"></i>
                          <strong>${s.original_filename}</strong>
                          <span class="badge badge-draft">v${s.version}</span>
                        </div>
                      </td>
                      <td>${s.project_title}</td>
                      <td>${s.student_name}</td>
                      <td>${new Date(s.submitted_at).toLocaleDateString()}</td>
                      <td>${scoreHtml}</td>
                      <td>
                        <div class="flex items-center gap-2">
                          <button class="btn btn-secondary btn-sm" onclick="ReportView.openBySubmission(${s.id})">
                            <i data-lucide="shield-check"></i> Report
                          </button>
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
      Toast.error('Submissions Error', err.message);
    }
  },

  async renderReports(container) {
    container.innerHTML = `
      <div class="flex items-center justify-between" style="margin-bottom: 2rem;">
        <div>
          <h1>Institutional Plagiarism Audit</h1>
          <p>System-wide similarity detection logs, cross-match documents, and originality scores.</p>
        </div>
        <button class="btn btn-primary" onclick="AdminView.handleBulkRecheck()">
          <i data-lucide="refresh-cw"></i> Re-Calculate All Similarity
        </button>
      </div>

      <div class="card" id="admin-reports-table-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading plagiarism audit...</div>
      </div>
    `;

    try {
      const reports = await API.get('/reports');
      const containerEl = document.getElementById('admin-reports-table-container');

      if (!reports || reports.length === 0) {
        containerEl.innerHTML = `<div class="empty-state"><p>No plagiarism reports generated yet.</p></div>`;
      } else {
        containerEl.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Project & Student</th>
                  <th>Document File</th>
                  <th>Similarity Score</th>
                  <th>Result Tag</th>
                  <th>Matched Sources</th>
                  <th>Processing Duration</th>
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
                        <div style="font-size:0.75rem; color:var(--text-muted);">${r.student_name} • ${r.department}</div>
                      </td>
                      <td>${r.original_filename} (v${r.submission_version})</td>
                      <td>
                        <span style="font-size:1.15rem; font-weight:800; color:${r.similarity_score < 20 ? 'var(--success)' : (r.similarity_score < 40 ? 'var(--warning)' : 'var(--danger)')};">
                          ${r.similarity_score}%
                        </span>
                      </td>
                      <td><span class="badge ${pillClass}">${r.result}</span></td>
                      <td><strong>${r.matched_documents_count}</strong> sources</td>
                      <td>${r.processing_time}s</td>
                      <td>
                        <div class="flex items-center gap-2">
                          <button class="btn btn-primary btn-sm" onclick="ReportView.open(${r.id})">
                            <i data-lucide="eye"></i> Inspect Report
                          </button>
                          <a href="${CONFIG.API_BASE_URL}/reports/${r.id}/download" target="_blank" class="btn btn-secondary btn-sm btn-icon" title="Print Export">
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

  async renderAuditLogs(container) {
    container.innerHTML = `
      <div style="margin-bottom: 2rem;">
        <h1>Security & Administrative Audit Trail</h1>
        <p>Immutable event log tracking logins, project creations, plagiarism checks, and supervisor reviews.</p>
      </div>

      <div class="card" id="admin-audit-logs-container">
        <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading audit logs...</div>
      </div>
    `;

    try {
      const logs = await API.get('/admin/audit-logs');
      const containerEl = document.getElementById('admin-audit-logs-container');

      if (!logs || logs.length === 0) {
        containerEl.innerHTML = `<div class="empty-state"><p>No audit events recorded yet.</p></div>`;
      } else {
        containerEl.innerHTML = `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Event ID</th>
                  <th>Action Code</th>
                  <th>Description</th>
                  <th>User</th>
                  <th>IP Address</th>
                  <th>Timestamp (UTC)</th>
                </tr>
              </thead>
              <tbody>
                ${logs.map(l => `
                  <tr>
                    <td><code>#${l.id}</code></td>
                    <td><span class="badge badge-submitted">${l.action}</span></td>
                    <td>${l.description}</td>
                    <td><strong>${l.user_name}</strong> (${l.user_email || 'system'})</td>
                    <td><code>${l.ip_address || '127.0.0.1'}</code></td>
                    <td>${new Date(l.created_at).toLocaleString()}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `;
      }
      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Audit Error', err.message);
    }
  },

  async renderSettings(container) {
    container.innerHTML = `
      <div style="margin-bottom: 2rem;">
        <h1>System Settings & Thresholds</h1>
        <p>Institutional configuration parameters and plagiarism detection sensitivity.</p>
      </div>

      <div class="card" style="max-width:800px;">
        <h3 class="card-title" style="margin-bottom:1.5rem;">Institutional Configuration</h3>
        <div id="settings-form-container">
          <div class="empty-state"><div class="spinner spinner-primary" style="margin:0 auto 1rem auto;"></div>Loading settings...</div>
        </div>
      </div>
    `;

    try {
      const settings = await API.get('/admin/settings');
      const formCont = document.getElementById('settings-form-container');

      formCont.innerHTML = `
        <form onsubmit="AdminView.saveSettings(event)">
          ${settings.map(s => `
            <div class="form-group">
              <label class="form-label">${s.description || s.key} (<code>${s.key}</code>)</label>
              <input type="text" class="form-control" name="${s.key}" value="${s.value}" required>
            </div>
          `).join('')}
          <button type="submit" class="btn btn-primary" style="margin-top:1rem;">
            <i data-lucide="save"></i> Save Configuration
          </button>
        </form>
      `;

      if (window.lucide) window.lucide.createIcons();
    } catch (err) {
      Toast.error('Settings Error', err.message);
    }
  },

  async saveSettings(e) {
    e.preventDefault();
    const form = e.target;
    const inputs = form.querySelectorAll('input[name]');

    try {
      for (const input of inputs) {
        await API.put(`/admin/settings/${input.name}`, { value: input.value });
      }
      Toast.success('Settings Saved', 'System configuration parameters updated.');
    } catch (err) {
      Toast.error('Save Failed', err.message);
    }
  },

  async handleBulkRecheck() {
    Modal.confirm({
      title: 'Trigger Bulk Similarity Re-Check',
      message: 'This will re-execute the TF-IDF and fingerprinting plagiarism engine across all submitted documents in the repository against the current corpus. Proceed?',
      confirmText: 'Run Re-Check',
      onConfirm: async () => {
        try {
          Toast.info('Analysis Started', 'Bulk similarity analysis initiated...');
          const res = await API.post('/admin/recheck-all-plagiarism');
          Toast.success('Completed', res.message);
          AdminView.renderDashboard(document.getElementById('main-content-view'));
        } catch (err) {
          Toast.error('Bulk Recheck Error', err.message);
        }
      }
    });
  },

  openCreateUserModal() {
    let modal = document.getElementById('admin-create-user-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'admin-create-user-modal';
      modal.className = 'modal-backdrop';
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="modal-dialog">
        <div class="modal-header">
          <h3 class="modal-title">Create New Institutional User</h3>
          <button class="modal-close-btn" onclick="Modal.close('admin-create-user-modal')">&times;</button>
        </div>
        <form onsubmit="AdminView.handleCreateUser(event)">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Full Name *</label>
              <input type="text" id="admin-new-name" class="form-control" placeholder="e.g. Dr. John Doe" required>
            </div>
            <div class="form-group">
              <label class="form-label">Email Address *</label>
              <input type="email" id="admin-new-email" class="form-control" placeholder="john.doe@example.com" required>
            </div>
            <div class="form-group">
              <label class="form-label">Temporary Password *</label>
              <input type="password" id="admin-new-pass" class="form-control" value="Password@12345" required>
            </div>
            <div class="grid grid-2 gap-3">
              <div class="form-group">
                <label class="form-label">Role *</label>
                <select id="admin-new-role" class="form-control" onchange="AdminView.toggleRoleFields(this.value)">
                  <option value="student">Student</option>
                  <option value="supervisor">Supervisor</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Department</label>
                <input type="text" id="admin-new-dept" class="form-control" value="Computer Science" required>
              </div>
            </div>
            <div class="form-group" id="admin-matric-group">
              <label class="form-label">Matriculation Number</label>
              <input type="text" id="admin-new-matric" class="form-control" placeholder="e.g. CSC/2023/2001">
            </div>
            <div class="form-group" id="admin-staffid-group" style="display:none;">
              <label class="form-label">Staff ID</label>
              <input type="text" id="admin-new-staffid" class="form-control" placeholder="e.g. STF/CSC/2020/099">
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" onclick="Modal.close('admin-create-user-modal')">Cancel</button>
            <button type="submit" class="btn btn-primary">Create User</button>
          </div>
        </form>
      </div>
    `;

    Modal.open('admin-create-user-modal');
  },

  toggleRoleFields(role) {
    const matricGroup = document.getElementById('admin-matric-group');
    const staffGroup = document.getElementById('admin-staffid-group');
    if (role === 'student') {
      if (matricGroup) matricGroup.style.display = 'block';
      if (staffGroup) staffGroup.style.display = 'none';
    } else if (role === 'supervisor') {
      if (matricGroup) matricGroup.style.display = 'none';
      if (staffGroup) staffGroup.style.display = 'block';
    } else {
      if (matricGroup) matricGroup.style.display = 'none';
      if (staffGroup) staffGroup.style.display = 'none';
    }
  },

  async handleCreateUser(e) {
    e.preventDefault();
    const role = document.getElementById('admin-new-role').value;
    const payload = {
      full_name: document.getElementById('admin-new-name').value,
      email: document.getElementById('admin-new-email').value,
      password: document.getElementById('admin-new-pass').value,
      role: role,
      department: document.getElementById('admin-new-dept').value,
      matric_number: role === 'student' ? document.getElementById('admin-new-matric').value : null,
      staff_id: role === 'supervisor' ? document.getElementById('admin-new-staffid').value : null
    };

    try {
      await API.post('/users', payload);
      Modal.close('admin-create-user-modal');
      Toast.success('User Created', `New ${role} account created successfully.`);
      AdminView.filterUsers();
    } catch (err) {
      Toast.error('Creation Failed', err.message);
    }
  },

  async openEditUserModal(userId) {
    let modal = document.getElementById('admin-edit-user-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'admin-edit-user-modal';
      modal.className = 'modal-backdrop';
      document.body.appendChild(modal);
    }

    try {
      const user = await API.get(`/users/${userId}`);
      modal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-header">
            <h3 class="modal-title">Edit User: ${user.full_name}</h3>
            <button class="modal-close-btn" onclick="Modal.close('admin-edit-user-modal')">&times;</button>
          </div>
          <form onsubmit="AdminView.handleEditUser(event, ${user.id})">
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">Full Name</label>
                <input type="text" id="edit-user-name" class="form-control" value="${user.full_name}" required>
              </div>
              <div class="form-group">
                <label class="form-label">Department</label>
                <input type="text" id="edit-user-dept" class="form-control" value="${user.department || ''}">
              </div>
              ${user.role === 'student' ? `
                <div class="form-group">
                  <label class="form-label">Matriculation Number</label>
                  <input type="text" id="edit-user-matric" class="form-control" value="${user.matric_number || ''}">
                </div>
              ` : ''}
              ${user.role === 'supervisor' ? `
                <div class="form-group">
                  <label class="form-label">Staff ID</label>
                  <input type="text" id="edit-user-staffid" class="form-control" value="${user.supervisor_profile ? (user.supervisor_profile.staff_id || '') : ''}">
                </div>
                <div class="form-group">
                  <label class="form-label">Specialization</label>
                  <input type="text" id="edit-user-spec" class="form-control" value="${user.supervisor_profile ? (user.supervisor_profile.specialization || '') : ''}">
                </div>
              ` : ''}
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" onclick="Modal.close('admin-edit-user-modal')">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Changes</button>
            </div>
          </form>
        </div>
      `;
      Modal.open('admin-edit-user-modal');
    } catch (err) {
      Toast.error('Error', err.message);
    }
  },

  async handleEditUser(e, userId) {
    e.preventDefault();
    const payload = {
      full_name: document.getElementById('edit-user-name').value,
      department: document.getElementById('edit-user-dept').value,
      matric_number: document.getElementById('edit-user-matric')?.value,
      staff_id: document.getElementById('edit-user-staffid')?.value,
      specialization: document.getElementById('edit-user-spec')?.value
    };

    try {
      await API.put(`/users/${userId}`, payload);
      Modal.close('admin-edit-user-modal');
      Toast.success('User Updated', 'User details updated successfully.');
      AdminView.filterUsers();
    } catch (err) {
      Toast.error('Update Failed', err.message);
    }
  },

  confirmDeleteUser(userId, userEmail) {
    Modal.confirm({
      title: 'Delete User Account',
      message: `Are you sure you want to permanently delete user account '${userEmail}'? All associated records will be removed.`,
      confirmText: 'Delete User',
      confirmClass: 'btn-danger',
      onConfirm: async () => {
        try {
          await API.delete(`/users/${userId}`);
          Toast.success('Deleted', `User '${userEmail}' removed.`);
          AdminView.filterUsers();
        } catch (err) {
          Toast.error('Delete Failed', err.message);
        }
      }
    });
  },

  async openAssignSupervisorModal(projectId, projectTitle) {
    let modal = document.getElementById('admin-assign-sup-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'admin-assign-sup-modal';
      modal.className = 'modal-backdrop';
      document.body.appendChild(modal);
    }

    try {
      const supervisors = await API.get('/supervisors');

      modal.innerHTML = `
        <div class="modal-dialog">
          <div class="modal-header">
            <h3 class="modal-title">Assign Supervisor to Project</h3>
            <button class="modal-close-btn" onclick="Modal.close('admin-assign-sup-modal')">&times;</button>
          </div>
          <form onsubmit="AdminView.handleAssignSupervisor(event, ${projectId})">
            <div class="modal-body">
              <p style="font-size:0.9rem; color:var(--text-main); margin-bottom:1rem;">
                Assigning supervisor for project: <strong>${projectTitle}</strong>
              </p>
              <div class="form-group">
                <label class="form-label">Select Faculty Supervisor *</label>
                <select id="assign-sup-select" class="form-control" required>
                  <option value="">-- Choose Supervisor --</option>
                  ${supervisors.map(s => `
                    <option value="${s.id}">
                      ${s.full_name} (${s.department || 'Faculty'}) - Current Load: ${s.assigned_count}/${s.max_students}
                    </option>
                  `).join('')}
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" onclick="Modal.close('admin-assign-sup-modal')">Cancel</button>
              <button type="submit" class="btn btn-primary">Confirm Assignment</button>
            </div>
          </form>
        </div>
      `;

      Modal.open('admin-assign-sup-modal');
    } catch (err) {
      Toast.error('Supervisors Error', err.message);
    }
  },

  async handleAssignSupervisor(e, projectId) {
    e.preventDefault();
    const supId = document.getElementById('assign-sup-select').value;
    if (!supId) return;

    try {
      await API.post(`/projects/${projectId}/assign-supervisor?supervisor_id=${supId}`);
      Modal.close('admin-assign-sup-modal');
      Toast.success('Supervisor Assigned', 'Faculty supervisor assigned and notifications dispatched.');
      AdminView.renderSupervisors(document.getElementById('main-content-view'));
    } catch (err) {
      Toast.error('Assignment Failed', err.message);
    }
  }
};
