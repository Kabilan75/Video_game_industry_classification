import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
});

export const getJobs = (params) =>
    client.get('/api/jobs', { params }).then(r => r.data);

export const getTopKeywords = (params) =>
    client.get('/api/keywords/top', { params }).then(r => r.data);

export const getTrends = (params) =>
    client.get('/api/trends', { params }).then(r => r.data);

export const getRegional = (params) =>
    client.get('/api/regional', { params }).then(r => r.data);

export default client;
