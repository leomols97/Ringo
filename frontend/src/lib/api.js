import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: `${BACKEND_URL}/api/private`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

api.interceptors.request.use(config => {
  if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
    const token = getCookie('csrftoken');
    if (token) config.headers['X-CSRFToken'] = token;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 403 && error.response?.data?.error === 'CSRF verification failed' && !error.config._csrfRetry) {
      error.config._csrfRetry = true;
      await initCsrf();
      const token = getCookie('csrftoken');
      if (token) error.config.headers['X-CSRFToken'] = token;
      return api(error.config);
    }
    return Promise.reject(error);
  }
);

export async function initCsrf() {
  await api.get('/auth/csrf/');
}

export default api;
