import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
});

// ── Jobs ──────────────────────────────────────────────────────────────────────
export const getJobs = (params) =>
    client.get('/api/jobs', { params }).then(r => r.data);

// ── Keywords ──────────────────────────────────────────────────────────────────
export const getTopKeywords = (params) =>
    client.get('/api/keywords/top', { params }).then(r => r.data);

// ── Trends ────────────────────────────────────────────────────────────────────
export const getTrends = (params) =>
    client.get('/api/trends', { params }).then(r => r.data);

export const getJobTrends = (params) =>
    client.get('/api/trends/jobs-over-time', { params }).then(r => r.data);

export const getEmergingSkills = (params) =>
    client.get('/api/trends/emerging', { params }).then(r => r.data);

export const getExperienceBreakdown = () =>
    client.get('/api/trends/experience-breakdown').then(r => r.data);

export const getDashboardStats = () =>
    client.get('/api/trends/dashboard-stats').then(r => r.data);

// ── Regional ──────────────────────────────────────────────────────────────────
export const getRegionalDistribution = (params) =>
    client.get('/api/regional/distribution', { params }).then(r => r.data);

export const getRegionalCompare = (params) =>
    client.get('/api/regional/compare', { params }).then(r => r.data);

export const getRegionalHeatmap = (params) =>
    client.get('/api/regional/heatmap', { params }).then(r => r.data);

// ── Export (CSV) ──────────────────────────────────────────────────────────────
export const buildExportUrl = (type, params = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== ''));
    return `${API_URL}/api/export/${type}${qs.toString() ? '?' + qs.toString() : ''}`;
};

export default client;
