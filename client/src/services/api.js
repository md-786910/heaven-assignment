import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: Add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle 401 errors (redirect to login)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stored auth data
      localStorage.removeItem("token");
      localStorage.removeItem("user");

      // Redirect to login with return URL
      const currentPath = window.location.pathname;
      if (
        currentPath !== "/login" &&
        currentPath !== "/register" &&
        currentPath !== "/forgot-password"
      ) {
        window.location.href = `/login?redirect=${encodeURIComponent(
          currentPath
        )}`;
      }
    }
    return Promise.reject(error);
  }
);

// Users API
export const usersAPI = {
  getAll: () => api.get("/users"),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post("/users", data),
};

// Issues API
export const issuesAPI = {
  getAll: (params) => api.get("/issues/", { params }),
  getById: (id) => api.get(`/issues/${id}`),
  create: (data) => api.post("/issues/", data),
  update: (id, data) => api.patch(`/issues/${id}`, data),
  delete: (id) => api.delete(`/issues/${id}`),
  bulkStatusUpdate: (data) => api.post("/issues/bulk-status", data),
  importCSV: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/issues/import", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getTimeline: (id) => api.get(`/issues/${id}/timeline`),
};

// Comments API
export const commentsAPI = {
  create: (issueId, data) => api.post(`/issues/${issueId}/comments`, data),
};

// Labels API
export const labelsAPI = {
  getAll: () => api.get("/labels"),
  create: (data) => api.post("/labels", data),
  replaceIssueLabels: (issueId, labelIds) =>
    api.put(`/labels/issues/${issueId}/labels`, labelIds),
};

// Reports API
export const reportsAPI = {
  getTopAssignees: (limit = 10) =>
    api.get(`/reports/top-assignees?limit=${limit}`),
  getLatency: () => api.get("/reports/latency"),
};

// Authentication API
export const authAPI = {
  login: (credentials) => api.post("/auth/login", credentials),
  register: (userData) => api.post("/auth/register", userData),
  requestPasswordReset: (email) => api.post("/auth/forgot-password", { email }),
  resetPassword: (data) => api.post("/auth/reset-password", data),
  logout: () => api.post("/auth/logout"),
  getCurrentUser: () => api.get("/auth/me"),
};

export default api;
