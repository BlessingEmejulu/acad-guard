/**
 * AcadGuard HTTP Fetch API Client Wrapper
 */
const API = {
  getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
  },

  async request(endpoint, options = {}) {
    const url = new URL(endpoint.startsWith('http') ? endpoint : `${CONFIG.API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`);
    
    // Append query parameters if present
    if (options.params) {
      Object.keys(options.params).forEach(key => {
        if (options.params[key] !== null && options.params[key] !== undefined && options.params[key] !== '') {
          url.searchParams.append(key, options.params[key]);
        }
      });
    }

    const headers = options.headers || {};
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!options.isFormData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const config = {
      method: options.method || 'GET',
      headers: headers,
      ...options
    };

    if (options.body && !options.isFormData && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url.toString(), config);

      if (response.status === 401) {
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.USER_KEY);
        if (!window.location.pathname.endsWith('login.html') && !window.location.pathname.endsWith('/login')) {
          Toast.error('Session Expired', 'Please login to continue.');
          setTimeout(() => {
            window.location.href = '/login';
          }, 800);
        }
        throw new Error('Unauthorized');
      }

      if (!response.ok) {
        let errorMsg = 'Request failed';
        try {
          const errData = await response.json();
          errorMsg = errData.detail || errData.message || errorMsg;
        } catch (_) {}
        throw new Error(errorMsg);
      }

      // Check if binary download or text
      const contentType = response.headers.get('content-type');
      if (contentType && (contentType.includes('application/octet-stream') || contentType.includes('application/pdf'))) {
        return response.blob();
      }

      return await response.json();
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  get(endpoint, params = {}) {
    return this.request(endpoint, { method: 'GET', params });
  },

  post(endpoint, body = {}) {
    return this.request(endpoint, { method: 'POST', body });
  },

  put(endpoint, body = {}) {
    return this.request(endpoint, { method: 'PUT', body });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  },

  upload(endpoint, formData) {
    return this.request(endpoint, {
      method: 'POST',
      body: formData,
      isFormData: true,
      headers: {} // Let browser set multipart boundary
    });
  }
};
