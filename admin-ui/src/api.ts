import axios from 'axios';

const ADMIN_API = 'http://localhost:8081';

// ---------- stockage des tokens ----------
const TOKEN_KEY = 'mp_access_token';
const REFRESH_KEY = 'mp_refresh_token';

export const tokenStore = {
  get access() {
    return sessionStorage.getItem(TOKEN_KEY);
  },
  get refresh() {
    return sessionStorage.getItem(REFRESH_KEY);
  },
  save(access: string, refresh: string) {
    sessionStorage.setItem(TOKEN_KEY, access);
    sessionStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_KEY);
  },
};

// ---------- client axios ----------
export const api = axios.create({
  baseURL: ADMIN_API,
  headers: { 'Content-Type': 'application/json' },
});

// injecte le token dans chaque requête
api.interceptors.request.use((config) => {
  const token = tokenStore.access;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// rafraîchit automatiquement le token si 401
let isRefreshing = false;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry && !isRefreshing) {
      original._retry = true;
      isRefreshing = true;

      try {
        const refresh = tokenStore.refresh;
        if (!refresh) throw new Error('no refresh token');

        const { data } = await axios.post(`${ADMIN_API}/admin/refresh`, {
          refresh_token: refresh,
        });

        tokenStore.save(data.access_token, data.refresh_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        isRefreshing = false;

        return api(original);          // rejoue la requête d'origine
      } catch {
        isRefreshing = false;
        tokenStore.clear();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// ---------- appels d'authentification ----------
export async function login(username: string, password: string) {
  // /admin/login attend un form-urlencoded (OAuth2PasswordRequestForm)
  const form = new URLSearchParams();
  form.append('username', username);
  form.append('password', password);

  const { data } = await axios.post(`${ADMIN_API}/admin/login`, form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  tokenStore.save(data.access_token, data.refresh_token);
  return data;
}

export async function getMe() {
  const { data } = await api.get('/admin/me');
  return data;
}

export function logout() {
  tokenStore.clear();
}
// ---------- données ----------
export async function getStats() {
  const { data } = await api.get('/admin/stats');
  return data;
}

export async function getUsers() {
  const { data } = await api.get('/admin/users');
  return data;
}

export async function getGenerations() {
  const { data } = await api.get('/admin/generations');
  return data;
}
// ---------- prompts LLM ----------
export async function getPrompts() {
  const { data } = await api.get('/admin/prompts');
  return data;
}

export async function getPrompt(id: number) {
  const { data } = await api.get(`/admin/prompts/${id}`);
  return data;
}

export async function updatePrompt(id: number, prompt: string) {
  const { data } = await api.put(`/admin/prompts/${id}`, { prompt });
  return data;
}

export async function getModels() {
  const { data } = await api.get('/admin/models');
  return data;
}

export async function updateConfig(
  configId: number,
  payload: { model_id?: number; temperature?: number; max_tokens?: number }
) {
  const { data } = await api.put(`/admin/configs/${configId}`, payload);
  return data;
}