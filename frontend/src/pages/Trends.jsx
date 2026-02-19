import React, { useState, useEffect } from 'react';
import { Loader2, Download, Flame, TrendingUp } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
    PieChart, Pie, Legend, AreaChart, Area, CartesianGrid,
    ScatterChart, Scatter, ZAxis
} from 'recharts';
import { getTopKeywords, getJobTrends, getEmergingSkills, getExperienceBreakdown, getRegionalHeatmap, buildExportUrl } from '../api/client';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1', '#14b8a6', '#f97316'];
const HEATMAP_LEVELS = [null, 'skills', 'software', 'experience'];

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#0d1117] border border-[#1e2d3d] rounded-lg px-3 py-2 text-sm shadow-xl">
                <p className="text-white font-medium">{label || payload[0].name}</p>
                <p className="text-blue-400">{payload[0].value} occurrences</p>
            </div>
        );
    }
    return null;
};

const CATEGORIES = [
    { key: null, label: 'All' },
    { key: 'skills', label: 'Skills' },
    { key: 'software', label: 'Software' },
    { key: 'experience', label: 'Experience' },
];

// ── Heatmap Component ──────────────────────────────────────────────────────────
const HeatmapCell = ({ value, max }) => {
    const intensity = max > 0 ? value / max : 0;
    const alpha = Math.max(0.08, intensity);
    return (
        <div
            className="rounded text-xs flex items-center justify-center font-mono border border-[#1e2d3d]"
            style={{
                backgroundColor: `rgba(59,130,246,${alpha})`,
                color: intensity > 0.5 ? '#fff' : '#94a3b8',
                minWidth: 32, minHeight: 28, padding: '2px 4px'
            }}
            title={value}
        >
            {value || ''}
        </div>
    );
};

const GeoHeatmap = ({ data }) => {
    // data = { regions: [...], keywords: [...], matrix: [{keyword, London: 5, ...}, ...] }
    if (!data || !data.regions || !data.matrix || data.matrix.length === 0) {
        return <p className="text-[#475569] text-sm py-6 text-center">Not enough data for geographic heatmap.</p>;
    }
    const { regions, matrix } = data;
    const allValues = matrix.flatMap(row => regions.map(r => row[r] || 0));
    const maxVal = Math.max(...allValues, 1);

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-xs">
                <thead>
                    <tr>
                        <th className="text-left px-2 py-1 text-[#475569] w-28 sticky left-0 bg-[#0d1117]">Skill / Region →</th>
                        {regions.map(r => (
                            <th key={r} className="px-1 py-1 text-[#94a3b8] font-normal text-center" style={{ minWidth: 60 }}>
                                <span className="block truncate">{r}</span>
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {matrix.map(row => (
                        <tr key={row.keyword}>
                            <td className="px-2 py-1 text-[#94a3b8] font-medium sticky left-0 bg-[#0d1117]">{row.keyword}</td>
                            {regions.map(r => (
                                <td key={r} className="px-1 py-1">
                                    <HeatmapCell value={row[r] || 0} max={maxVal} />
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

const Trends = () => {
    const [keywords, setKeywords] = useState([]);
    const [jobTrends, setJobTrends] = useState([]);
    const [emerging, setEmerging] = useState([]);
    const [expBreakdown, setExpBreakdown] = useState([]);
    const [heatmapData, setHeatmapData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeCategory, setActiveCategory] = useState(null);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const params = { limit: 20 };
                if (activeCategory) params.category = activeCategory;

                const [kwData, trendsData, emData, expData, hmData] = await Promise.all([
                    getTopKeywords(params),
                    getJobTrends({ days: 90 }),
                    getEmergingSkills({ limit: 8, ...(activeCategory ? { category: activeCategory } : {}) }),
                    getExperienceBreakdown(),
                    getRegionalHeatmap({ limit_regions: 8, limit_keywords: 12, ...(activeCategory ? { category: activeCategory } : {}) }),
                ]);

                setKeywords(kwData.keywords || []);
                const formatted = (trendsData.data || []).map(d => ({
                    ...d,
                    date: new Date(d.date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
                }));
                setJobTrends(formatted);
                setEmerging(emData.emerging || []);
                setExpBreakdown(expData.breakdown || []);
                setHeatmapData(hmData);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [activeCategory]);

    const barData = keywords.slice(0, 15).map(k => ({ name: k.keyword, value: k.total_frequency }));
    const pieData = keywords.slice(0, 8).map(k => ({ name: k.keyword, value: k.job_count }));

    const csvParams = activeCategory ? { category: activeCategory } : {};

    return (
        <div className="space-y-6">
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">
                        Keyword <span className="gradient-text">Trends</span>
                    </h1>
                    <p className="text-[#64748b] text-sm mt-1">Most in-demand skills across UK games industry jobs</p>
                </div>
                <a
                    href={buildExportUrl('keywords', csvParams)}
                    download
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0d1117] border border-[#1e2d3d] text-sm text-[#94a3b8] hover:text-white hover:border-[#334155] transition-all"
                >
                    <Download className="w-4 h-4" /> Export CSV
                </a>
            </div>

            {/* Category tabs */}
            <div className="flex gap-2">
                {CATEGORIES.map(cat => (
                    <button
                        key={cat.key ?? 'all'}
                        onClick={() => setActiveCategory(cat.key)}
                        className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${activeCategory === cat.key
                            ? 'bg-blue-600 text-white'
                            : 'bg-[#0d1117] border border-[#1e2d3d] text-[#94a3b8] hover:text-white hover:border-[#334155]'
                            }`}
                    >
                        {cat.label}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="flex justify-center py-20">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                </div>
            ) : (
                <div className="space-y-6">
                    {/* Time Series Chart */}
                    <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                        <h2 className="text-sm font-semibold text-white mb-1">New Jobs Over Time (Last 90 Days)</h2>
                        <p className="text-xs text-[#475569] mb-4">Daily volume of new job listings</p>
                        <div className="h-[200px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={jobTrends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" vertical={false} />
                                    <XAxis dataKey="date" tick={{ fill: '#475569', fontSize: 10 }} axisLine={false} tickLine={false} minTickGap={30} />
                                    <YAxis tick={{ fill: '#475569', fontSize: 10 }} axisLine={false} tickLine={false} width={30} />
                                    <Tooltip contentStyle={{ backgroundColor: '#0d1117', borderColor: '#1e2d3d', color: '#fff' }} itemStyle={{ color: '#3b82f6' }} />
                                    <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorCount)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Bar + Pie */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                        {/* Bar chart */}
                        <div className="xl:col-span-2 rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                            <h2 className="text-sm font-semibold text-white mb-1">Frequency by Keyword</h2>
                            <p className="text-xs text-[#475569] mb-4">Total mentions across all job descriptions</p>
                            <ResponsiveContainer width="100%" height={340}>
                                <BarChart data={barData} layout="vertical" margin={{ left: 0, right: 20 }}>
                                    <XAxis type="number" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                                    <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} width={110} axisLine={false} tickLine={false} />
                                    <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                        {barData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Pie chart */}
                        <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                            <h2 className="text-sm font-semibold text-white mb-1">Job Coverage</h2>
                            <p className="text-xs text-[#475569] mb-4">% of jobs mentioning top skills</p>
                            <ResponsiveContainer width="100%" height={340}>
                                <PieChart>
                                    <Pie data={pieData} cx="50%" cy="45%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value">
                                        {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                    </Pie>
                                    <Tooltip content={<CustomTooltip />} />
                                    <Legend formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 11 }}>{value}</span>} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Emerging Skills + Experience Breakdown */}
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        {/* Emerging / Fast-growing skills */}
                        <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                            <div className="flex items-center gap-2 mb-1">
                                <Flame className="w-4 h-4 text-orange-400" />
                                <h2 className="text-sm font-semibold text-white">Emerging Skills</h2>
                            </div>
                            <p className="text-xs text-[#475569] mb-4">Fastest-growing this week vs last week</p>
                            {emerging.length === 0 ? (
                                <p className="text-[#475569] text-sm py-8 text-center">Not enough data for this period yet.</p>
                            ) : (
                                <div className="space-y-2">
                                    {emerging.map((item, i) => (
                                        <div key={item.keyword} className="flex items-center gap-3">
                                            <span className="text-xs text-[#475569] w-4">{i + 1}</span>
                                            <div className="flex-1">
                                                <div className="flex items-center justify-between mb-0.5">
                                                    <span className="text-sm text-white font-medium">{item.keyword}</span>
                                                    <span className={`text-xs font-bold ${item.growth_pct > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                                        {item.growth_pct > 0 ? '+' : ''}{item.growth_pct}%
                                                    </span>
                                                </div>
                                                <div className="flex gap-2 text-xs text-[#475569]">
                                                    <span>This week: {item.this_week}</span>
                                                    <span>·</span>
                                                    <span>Last week: {item.last_week}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Experience Level Breakdown */}
                        <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                            <div className="flex items-center gap-2 mb-1">
                                <TrendingUp className="w-4 h-4 text-purple-400" />
                                <h2 className="text-sm font-semibold text-white">Experience Level Demand</h2>
                            </div>
                            <p className="text-xs text-[#475569] mb-4">Jobs mentioning each seniority level</p>
                            {expBreakdown.length === 0 ? (
                                <p className="text-[#475569] text-sm py-8 text-center">No experience level data yet.</p>
                            ) : (
                                <ResponsiveContainer width="100%" height={280}>
                                    <BarChart data={expBreakdown.slice(0, 10)} layout="vertical" margin={{ left: 0, right: 20 }}>
                                        <XAxis type="number" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                                        <YAxis type="category" dataKey="level" tick={{ fill: '#94a3b8', fontSize: 11 }} width={90} axisLine={false} tickLine={false} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0d1117', borderColor: '#1e2d3d', color: '#fff' }}
                                            formatter={(v) => [`${v} jobs`, 'Count']}
                                        />
                                        <Bar dataKey="job_count" radius={[0, 4, 4, 0]}>
                                            {expBreakdown.slice(0, 10).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            )}
                        </div>
                    </div>

                    {/* Geographic Skills × Region Heatmap */}
                    <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                        <h2 className="text-sm font-semibold text-white mb-1">🗺️ Skills × Region Heatmap</h2>
                        <p className="text-xs text-[#475569] mb-4">Job demand for top skills across UK regions (darker blue = more jobs)</p>
                        <GeoHeatmap data={heatmapData} />
                    </div>

                    {/* Full Keyword Table */}
                    <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] overflow-hidden">
                        <div className="p-5 border-b border-[#1e2d3d] flex items-center justify-between">
                            <h2 className="text-sm font-semibold text-white">Full Keyword Rankings</h2>
                            <a
                                href={buildExportUrl('keywords', csvParams)}
                                download
                                className="flex items-center gap-1.5 text-xs text-[#64748b] hover:text-white transition-colors"
                            >
                                <Download className="w-3.5 h-3.5" /> Download CSV
                            </a>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-[#1e2d3d]">
                                        <th className="text-left px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">#</th>
                                        <th className="text-left px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">Keyword</th>
                                        <th className="text-left px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">Category</th>
                                        <th className="text-right px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">Jobs</th>
                                        <th className="text-right px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">Mentions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {keywords.map((k, i) => (
                                        <tr key={k.keyword} className="border-b border-[#0f1629] hover:bg-[#111827] transition-colors">
                                            <td className="px-5 py-3 text-[#475569]">{i + 1}</td>
                                            <td className="px-5 py-3 font-medium text-white">{k.keyword}</td>
                                            <td className="px-5 py-3">
                                                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${k.category === 'skills' ? 'bg-blue-500/10 text-blue-400' :
                                                    k.category === 'software' ? 'bg-purple-500/10 text-purple-400' :
                                                        'bg-amber-500/10 text-amber-400'
                                                    }`}>
                                                    {k.category}
                                                </span>
                                            </td>
                                            <td className="px-5 py-3 text-right text-[#94a3b8]">{k.job_count}</td>
                                            <td className="px-5 py-3 text-right text-[#94a3b8]">{k.total_frequency}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Trends;
