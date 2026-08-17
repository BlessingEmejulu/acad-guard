/**
 * Sidebar and Top Navbar Component Manager
 */
const Navbar = {
  renderSidebar(role, activeRoute) {
    const sidebarContainer = document.getElementById('sidebar-navigation');
    if (!sidebarContainer) return;

    let navHtml = '';

    if (role === 'student') {
      navHtml = `
        <div class="menu-section-title">Main Menu</div>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'student/dashboard' ? 'active' : ''}" onclick="Router.navigate('student/dashboard')">
            <i data-lucide="layout-dashboard"></i> <span>Dashboard</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'student/projects' ? 'active' : ''}" onclick="Router.navigate('student/projects')">
            <i data-lucide="folder-git-2"></i> <span>My Projects</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'student/reports' ? 'active' : ''}" onclick="Router.navigate('student/reports')">
            <i data-lucide="shield-check"></i> <span>Plagiarism Reports</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'student/profile' ? 'active' : ''}" onclick="Router.navigate('student/profile')">
            <i data-lucide="user"></i> <span>Profile</span>
          </a>
        </li>
      `;
    } else if (role === 'supervisor') {
      navHtml = `
        <div class="menu-section-title">Supervisor Portal</div>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'supervisor/dashboard' ? 'active' : ''}" onclick="Router.navigate('supervisor/dashboard')">
            <i data-lucide="layout-dashboard"></i> <span>Dashboard</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'supervisor/students' ? 'active' : ''}" onclick="Router.navigate('supervisor/students')">
            <i data-lucide="users"></i> <span>Assigned Students</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'supervisor/projects' ? 'active' : ''}" onclick="Router.navigate('supervisor/projects')">
            <i data-lucide="folder-check"></i> <span>Projects Review</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'supervisor/reports' ? 'active' : ''}" onclick="Router.navigate('supervisor/reports')">
            <i data-lucide="file-search"></i> <span>Plagiarism Reports</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'supervisor/profile' ? 'active' : ''}" onclick="Router.navigate('supervisor/profile')">
            <i data-lucide="user"></i> <span>Profile</span>
          </a>
        </li>
      `;
    } else if (role === 'admin') {
      navHtml = `
        <div class="menu-section-title">System Administration</div>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'admin/dashboard' ? 'active' : ''}" onclick="Router.navigate('admin/dashboard')">
            <i data-lucide="layout-dashboard"></i> <span>Admin Dashboard</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'admin/users' ? 'active' : ''}" onclick="Router.navigate('admin/users')">
            <i data-lucide="users"></i> <span>User Management</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'admin/supervisors' ? 'active' : ''}" onclick="Router.navigate('admin/supervisors')">
            <i data-lucide="user-check"></i> <span>Supervisor Allocation</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'admin/projects' ? 'active' : ''}" onclick="Router.navigate('admin/projects')">
            <i data-lucide="folder-kanban"></i> <span>All Projects</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'admin/submissions' ? 'active' : ''}" onclick="Router.navigate('admin/submissions')">
            <i data-lucide="file-stack"></i> <span>All Submissions</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'admin/reports' ? 'active' : ''}" onclick="Router.navigate('admin/reports')">
            <i data-lucide="shield-alert"></i> <span>Plagiarism Audit</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'admin/audit-logs' ? 'active' : ''}" onclick="Router.navigate('admin/audit-logs')">
            <i data-lucide="history"></i> <span>Audit Trail</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${activeRoute === 'admin/settings' ? 'active' : ''}" onclick="Router.navigate('admin/settings')">
            <i data-lucide="settings"></i> <span>System Settings</span>
          </a>
        </li>
      `;
    }

    sidebarContainer.innerHTML = navHtml;

    // Update user profile widget in sidebar
    const user = Auth.getUser();
    if (user) {
      const nameEl = document.getElementById('sidebar-user-name');
      const roleEl = document.getElementById('sidebar-user-role');
      const avatarEl = document.getElementById('sidebar-user-avatar');
      if (nameEl) nameEl.textContent = user.full_name;
      if (roleEl) roleEl.textContent = user.role.toUpperCase();
      if (avatarEl) avatarEl.textContent = user.full_name.charAt(0).toUpperCase();
    }

    // Refresh Lucide icons
    if (window.lucide) {
      window.lucide.createIcons();
    }
  },

  async loadNotifications() {
    try {
      const notifs = await API.get('/notifications');
      const unread = notifs.filter(n => !n.is_read).length;
      const badge = document.getElementById('notification-badge');
      if (badge) {
        if (unread > 0) {
          badge.textContent = unread > 9 ? '9+' : unread;
          badge.style.display = 'flex';
        } else {
          badge.style.display = 'none';
        }
      }

      // Render dropdown list
      const listEl = document.getElementById('notifications-dropdown-list');
      if (listEl) {
        if (notifs.length === 0) {
          listEl.innerHTML = '<div style="padding:1.5rem; text-align:center; color:var(--text-muted); font-size:0.85rem;">No new notifications</div>';
        } else {
          listEl.innerHTML = notifs.map(n => `
            <div class="notification-item ${n.is_read ? 'read' : 'unread'}" style="padding:0.75rem 1rem; border-bottom:1px solid var(--border-light); background:${n.is_read ? '#ffffff' : '#f0f9ff'};" onclick="Navbar.readNotification(${n.id})">
              <div style="font-weight:600; font-size:0.85rem; color:var(--text-main);">${n.title}</div>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">${n.message}</div>
              <div style="font-size:0.7rem; color:var(--text-light); margin-top:4px;">${new Date(n.created_at).toLocaleString()}</div>
            </div>
          `).join('');
        }
      }
    } catch (_) {}
  },

  async readNotification(id) {
    try {
      await API.put(`/notifications/${id}/read`);
      this.loadNotifications();
    } catch (_) {}
  },

  async readAllNotifications() {
    try {
      await API.put('/notifications/read-all');
      this.loadNotifications();
      Toast.success('Notifications', 'All marked as read.');
    } catch (_) {}
  },

  toggleNotificationDropdown() {
    const dropdown = document.getElementById('notifications-popover');
    if (dropdown) {
      dropdown.classList.toggle('active');
    }
  },

  toggleMobileSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.classList.toggle('open');
    }
  }
};
