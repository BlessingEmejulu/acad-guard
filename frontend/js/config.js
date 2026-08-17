/**
 * AcadGuard Global Configuration and Constants
 */
const CONFIG = {
  API_BASE_URL: window.location.origin + '/api',
  TOKEN_KEY: 'acadguard_access_token',
  USER_KEY: 'acadguard_user_data',
  FILE_MAX_SIZE_MB: 25,
  ALLOWED_EXTENSIONS: ['.pdf', '.docx', '.doc', '.txt'],
  POLL_INTERVAL_MS: 30000, // Background notification check
};
