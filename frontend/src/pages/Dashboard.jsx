import React, { useState, useEffect } from 'react';
import { Briefcase, Tag, TrendingUp, MapPin, Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import StatsCard from '../components/StatsCard';
import { getJobs, getTopKeywords } from '../api/client';

const CHART_COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#0d1117] border border-[#1e2d3d] rounded-lg px-3 py-2 text-sm shadow-xl">
                <p className="text-white font-medium">{label}</p>
                <p className="text-blue-400">{payload[0].value} jobs</p>
            </div>
        );
    }
    return null;
};

const Dashboard = () => {
    const [stats, setStats] = useState({ total: 0, locations: 0, keywords: 0 });
    const [keywords, setKeywords] = useState([]);
    const [recentJobs, setRecentJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const [jobsData, kwData] = await Promise.all([
                    getJobs({ page: 1, page_size: 5 }),
                    getTopKeywords({ limit: 12 }),
                ]);
                setStats({
                    total: jobsData.total,
                    locations: new Set(jobsData.items.map(j => j.location)).size,
                    keywords: kwData.keywords?.length || 0,
                });
                setRecentJobs(jobsData.items);
                setKeywords(kwData.keywords || []);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const chartData = keywords.slice(0, 10).map(k => ({
        name: k.keyword,
        jobs: k.job_count,
    }));

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-white">
                    UK Games Industry <span className="gradient-text">Overview</span>
                </h1>
                <p className="text-[#64748b] text-sm mt-1">
                    Real-time analysis of UK games industry job market
                </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard title="Total Jobs" value={stats.total} icon={Briefcase} color="blue" subtitle="Active listings" />
                <StatsCard title="Top Keywords" value={keywords.length} icon={Tag} color="purple" subtitle="Tracked skills" />
                <StatsCard title="UK Locations" value={stats.locations} icon={MapPin} color="emerald" subtitle="Cities covered" />
                <StatsCard title="Data Source" value="Live" icon={TrendingUp} color="amber" subtitle="Hitmarker.net" />
            </div>

            {/* Charts + Recent Jobs */}
            <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
                {/* Bar Chart */}
                <div className="xl:col-span-3 rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                    <h2 className="text-sm font-semibold text-white mb-1">Top In-Demand Skills</h2>
                    <p className="text-xs text-[#475569] mb-4">Number of job listings mentioning each skill</p>
                    {chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={260}>
                            <BarChart data={chartData} layout="vertical" margin={{ left: 0, right: 20 }}>
                                <XAxis type="number" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                                <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} width={100} axisLine={false} tickLine={false} />
                                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                                <Bar dataKey="jobs" radius={[0, 4, 4, 0]}>
                                    {chartData.map((_, i) => (
                                        <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="flex items-center justify-center h-48 text-[#475569] text-sm">
                            No keyword data yet. Run the scraper to populate.
                        </div>
                    )}
                </div>

                {/* Recent Jobs */}
                <div className="xl:col-span-2 rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                    <h2 className="text-sm font-semibold text-white mb-1">Recent Listings</h2>
                    <p className="text-xs text-[#475569] mb-4">Latest UK game industry jobs</p>
                    <div className="space-y-3">
                        {recentJobs.map(job => (
                            <a
                                key={job.id}
                                href={job.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block p-3 rounded-lg border border-[#1e2d3d] hover:border-blue-500/30 hover:bg-[#111827] transition-all group"
                            >
                                <p className="text-sm font-medium text-white group-hover:text-blue-400 truncate transition-colors">
                                    {job.title}
                                </p>
                                <p className="text-xs text-[#64748b] mt-0.5">{job.company} · {job.location}</p>
                            </a>
                        ))}
                    </div>
                </div>
            </div>

            {/* Keyword pills */}
            <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                <h2 className="text-sm font-semibold text-white mb-3">All Tracked Keywords</h2>
                <div className="flex flex-wrap gap-2">
                    {keywords.map((k, i) => (
                        <span
                            key={k.keyword}
                            className="px-3 py-1 rounded-full text-xs font-medium border"
                            style={{
                                backgroundColor: `${CHART_COLORS[i % CHART_COLORS.length]}15`,
                                borderColor: `${CHART_COLORS[i % CHART_COLORS.length]}30`,
                                color: CHART_COLORS[i % CHART_COLORS.length],
                            }}
                        >
                            {k.keyword} <span className="opacity-60">({k.job_count})</span>
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
