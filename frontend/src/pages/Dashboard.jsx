import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Tag, TrendingUp, MapPin, Loader2, Search, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import StatsCard from '../components/StatsCard';
import { getJobs, getTopKeywords, getDashboardStats } from '../api/client';

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

const DeltaBadge = ({ delta, pct }) => {
    if (delta === 0 || delta == null) return (
        <span className="flex items-center gap-1 text-xs text-[#64748b]"><Minus className="w-3 h-3" /> No change</span>
    );
    const positive = delta > 0;
    return (
        <span className={`flex items-center gap-1 text-xs font-medium ${positive ? 'text-emerald-400' : 'text-red-400'}`}>
            {positive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {positive ? '+' : ''}{delta} ({pct > 0 ? '+' : ''}{pct}%) vs last week
        </span>
    );
};

const Dashboard = () => {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');
    const [stats, setStats] = useState({ total: 0, locations: 0, keywords: 0 });
    const [keywords, setKeywords] = useState([]);
    const [recentJobs, setRecentJobs] = useState([]);
    const [weekStats, setWeekStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const [jobsData, kwData, weekData] = await Promise.all([
                    getJobs({ page: 1, page_size: 5 }),
                    getTopKeywords({ limit: 12 }),
                    getDashboardStats(),
                ]);
                setStats({
                    total: jobsData.total,
                    locations: new Set(jobsData.items.map(j => j.location)).size,
                    keywords: kwData.keywords?.length || 0,
                });
                setRecentJobs(jobsData.items);
                setKeywords(kwData.keywords || []);
                setWeekStats(weekData);
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

            {/* Search Bar */}
            <div className="relative">
                <input
                    type="text"
                    placeholder="Search relevant jobs in London..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            navigate(`/jobs?keyword=${searchQuery}&location=London`);
                        }
                    }}
                    className="w-full bg-[#0d1117] border border-[#1e2d3d] rounded-xl py-4 pl-12 pr-4 text-white focus:outline-none focus:border-blue-500/50 transition-colors"
                />
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#64748b]" />
                <button
                    onClick={() => navigate(`/jobs?keyword=${searchQuery}&location=London`)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                    Search
                </button>
            </div>

            {/* Stats with change indicators */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-[#64748b] uppercase tracking-wide">Total Jobs</span>
                        <Briefcase className="w-4 h-4 text-blue-400" />
                    </div>
                    <p className="text-2xl font-bold text-white mb-1">{stats.total}</p>
                    {weekStats && <DeltaBadge delta={weekStats.delta} pct={weekStats.delta_pct} />}
                </div>
                <StatsCard title="Top Keywords" value={keywords.length} icon={Tag} color="purple" subtitle="Tracked skills" />
                <StatsCard title="UK Locations" value={stats.locations} icon={MapPin} color="emerald" subtitle="Cities covered" />
                <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-[#64748b] uppercase tracking-wide">This Week</span>
                        <TrendingUp className={`w-4 h-4 ${weekStats?.trend === 'up' ? 'text-emerald-400' : weekStats?.trend === 'down' ? 'text-red-400' : 'text-amber-400'}`} />
                    </div>
                    <p className="text-2xl font-bold text-white mb-1">{weekStats?.this_week_jobs ?? '—'}</p>
                    <p className="text-xs text-[#64748b]">new listings</p>
                </div>
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
