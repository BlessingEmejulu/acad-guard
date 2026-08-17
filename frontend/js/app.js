/**
 * AcadGuard Main Application Router & Controller
 */
const Router = {
  currentRoute: null,

  init() {
    // Check authentication
    if (!Auth.isLoggedIn()) {
      window.location.href = '/login';
      return;
    }

    const user = Auth.getUser();
    const role = user.role;

    // Listen to browser back/forward and hash changes
    window.addEventListener('hashchange', () => this.handleHashChange());

    // Initial navigation based on URL or default role route
    const hash = window.location.hash.replace(/^#\/?/, '');
    if (hash) {
      this.navigate(hash, false);
    } else {
      const defaultRoute = role === 'student' ? 'student/dashboard' : (role === 'supervisor' ? 'supervisor/dashboard' : 'admin/dashboard');
      this.navigate(defaultRoute, true);
    }

    // Initialize notification polling
    Navbar.loadNotifications();
    setInterval(() => Navbar.loadNotifications(), CONFIG.POLL_INTERVAL_MS);

    // Global click listener to close dropdowns
    document.addEventListener('click', (e) => {
      const popover = document.getElementById('notifications-popover');
      const bellBtn = document.getElementById('notification-bell-btn');
      if (popover && popover.classList.contains('active')) {
        if (!popover.contains(e.target) && !bellBtn.contains(e.target)) {
          popover.classList.remove('active');
        }
      }
    });
  },

  handleHashChange() {
    const hash = window.location.hash.replace(/^#\/?/, '');
    if (hash && hash !== this.currentRoute) {
      this.navigate(hash, false);
    }
  },

  navigate(route, updateHash = true) {
    if (!Auth.isLoggedIn()) {
      window.location.href = '/login';
      return;
    }

    const user = Auth.getUser();
    const role = user.role;
    this.currentRoute = route;

    if (updateHash) {
      window.location.hash = `#/${route}`;
    }

    // Update sidebar active link
    Navbar.renderSidebar(role, route);

    const mainContainer = document.getElementById('main-content-view');
    if (!mainContainer) return;

    // Close mobile drawer if open
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) sidebar.classList.remove('open');

    // Route matching
    const [section, action, id] = route.split('/');

    if (role === 'student') {
      if (section === 'student' && action === 'dashboard') {
        StudentView.renderDashboard(mainContainer);
      } else if (section === 'student' && action === 'projects') {
        if (id) {
          StudentView.renderProjectDetail(parseInt(id));
        } else {
          StudentView.renderProjects(mainContainer);
        }
      } else if (section === 'student' && action === 'reports') {
        StudentView.renderReports(mainContainer);
      } else if (section === 'student' && action === 'profile') {
        StudentView.renderProfile(mainContainer);
      } else {
        StudentView.renderDashboard(mainContainer);
      }
    } else if (role === 'supervisor') {
      if (section === 'supervisor' && action === 'dashboard') {
        SupervisorView.renderDashboard(mainContainer);
      } else if (section === 'supervisor' && action === 'students') {
        SupervisorView.renderStudents(mainContainer);
      } else if (section === 'supervisor' && action === 'projects') {
        SupervisorView.renderProjects(mainContainer);
      } else if (section === 'supervisor' && action === 'reports') {
        SupervisorView.renderReports(mainContainer);
      } else if (section === 'supervisor' && action === 'profile') {
        SupervisorView.renderProfile(mainContainer);
      } else {
        SupervisorView.renderDashboard(mainContainer);
      }
    } else if (role === 'admin') {
      if (section === 'admin' && action === 'dashboard') {
        AdminView.renderDashboard(mainContainer);
      } else if (section === 'admin' && action === 'users') {
        AdminView.renderUsers(mainContainer);
      } else if (section === 'admin' && action === 'supervisors') {
        AdminView.renderSupervisors(mainContainer);
      } else if (section === 'admin' && action === 'projects') {
        AdminView.renderProjects(mainContainer);
      } else if (section === 'admin' && action === 'submissions') {
        AdminView.renderSubmissions(mainContainer);
      } else if (section === 'admin' && action === 'reports') {
        AdminView.renderReports(mainContainer);
      } else if (section === 'admin' && action === 'audit-logs') {
        AdminView.renderAuditLogs(mainContainer);
      } else if (section === 'admin' && action === 'settings') {
        AdminView.renderSettings(mainContainer);
      } else {
        AdminView.renderDashboard(mainContainer);
      }
    }

    // Scroll to top
    window.scrollTo(0, 0);
  }
};

// Bootstrap application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('app-root')) {
    Router.init();
  }
});
