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

export const getRegionalDistribution = (params) =>
    client.get('/api/regional/distribution', { params }).then(r => r.data);

export const getRegionalCompare = (params) =>
    client.get('/api/regional/compare', { params }).then(r => r.data);

export default client;
