import axios from 'axios';

const configuredBaseURL = process.env.NEXT_PUBLIC_API_URL || '/api';
const normalizedBaseURL = configuredBaseURL.replace(/\/+$/, '');
const baseURL = normalizedBaseURL.endsWith('/api')
  ? normalizedBaseURL
  : `${normalizedBaseURL}/api`;

const apiClient = axios.create({
  baseURL,
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  if (typeof window === 'undefined') {
    return config;
  }

  const cookieValue = document.cookie
    .split('; ')
    .find((entry) => entry.startsWith('access_token='));

  if (cookieValue) {
    const token = decodeURIComponent(cookieValue.split('=')[1]);
    config.params = {
      ...config.params,
      token,
    };

    if (config.headers) {
      config.headers.set('Authorization', `Bearer ${token}`);
    } else {
      config.headers = new axios.AxiosHeaders({
        Authorization: `Bearer ${token}`,
      });
    }
  }

  return config;
});

export default apiClient;
