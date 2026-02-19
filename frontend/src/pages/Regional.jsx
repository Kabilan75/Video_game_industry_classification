import React, { useState, useEffect } from 'react';
import { Loader2, MapPin, Download, Printer } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend,
} from 'recharts';
import { getRegionalDistribution, getRegionalCompare, buildExportUrl } from '../api/client';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];

// UK regions highlighted in the project brief
const COMPARE_REGIONS = ['Leicester', 'London', 'Nottingham', 'Leamington Spa'];

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#0d1117] border border-[#1e2d3d] rounded-lg px-3 py-2 text-sm shadow-xl">
                <p className="text-white font-medium">{label || payload[0].name}</p>
                {payload.map((p, i) => (
                    <p key={i} style={{ color: p.color }}>{p.name}: {p.value}</p>
                ))}
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

const Regional = () => {
    const [distribution, setDistribution] = useState([]);
    const [comparison, setComparison] = useState({});
    const [loading, setLoading] = useState(true);
    const [compareLoading, setCompareLoading] = useState(true);
    const [activeCategory, setActiveCategory] = useState(null);
    const [error, setError] = useState(null);

    // Fetch overall regional distribution
    useEffect(() => {
        setLoading(true);
        getRegionalDistribution({ category: activeCategory || undefined })
            .then(data => setDistribution(data.distribution || []))
            .catch(() => setError('Failed to load regional data. Is the backend running?'))
            .finally(() => setLoading(false));
    }, [activeCategory]);

    // Fetch comparison for the 4 key regions
    useEffect(() => {
        setCompareLoading(true);
        getRegionalCompare({ regions: COMPARE_REGIONS.join(',') })
            .then(data => setComparison(data.comparison || {}))
            .catch(() => setComparison({}))
            .finally(() => setCompareLoading(false));
    }, []);

    // Build radar chart data for top skills across key regions
    const radarKeywords = Array.from(
        new Set(
            Object.values(comparison)
                .flat()
                .slice(0, 8)
                .map(k => k.keyword)
        )
    );

    const radarData = radarKeywords.map(keyword => {
        const point = { keyword };
        COMPARE_REGIONS.forEach(region => {
            const match = (comparison[region] || []).find(k => k.keyword === keyword);
            point[region] = match ? match.count : 0;
        });
        return point;
    });

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">
                        Regional <span className="gradient-text">Analysis</span>
                    </h1>
                    <p className="text-[#64748b] text-sm mt-1">
                        Geographic distribution of UK games industry jobs and skills
                    </p>
                </div>
                <div className="flex gap-2">
                    <a
                        href={buildExportUrl('regional')}
                        download
                        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[#0d1117] border border-[#1e2d3d] text-sm text-[#94a3b8] hover:text-white hover:border-[#334155] transition-all"
                        title="Download regional data as CSV"
                    >
                        <Download className="w-4 h-4" /> CSV
                    </a>
                    <button
                        onClick={() => window.print()}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[#0d1117] border border-[#1e2d3d] text-sm text-[#94a3b8] hover:text-white hover:border-[#334155] transition-all"
                        title="Print / Save as PDF"
                    >
                        <Printer className="w-4 h-4" /> Print
                    </button>
                </div>
            </div>

            {/* Category filter */}
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

            {error && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
                    {error}
                </div>
            )}

            {/* Section 1: UK-wide distribution bar chart */}
            <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                <h2 className="text-sm font-semibold text-white mb-1">Jobs by Region (UK-wide)</h2>
                <p className="text-xs text-[#475569] mb-4">Number of active job listings per location</p>
                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                ) : distribution.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-16 text-[#475569]">
                        <MapPin className="w-8 h-8 mb-2 opacity-40" />
                        <p className="text-sm">No regional data yet. Run the scraper to populate.</p>
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height={Math.max(260, distribution.slice(0, 20).length * 28)}>
                        <BarChart
                            data={distribution.slice(0, 20)}
                            layout="vertical"
                            margin={{ left: 0, right: 30 }}
                        >
                            <XAxis type="number" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <YAxis
                                type="category"
                                dataKey="region"
                                tick={{ fill: '#94a3b8', fontSize: 11 }}
                                width={120}
                                axisLine={false}
                                tickLine={false}
                            />
                            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                            <Bar dataKey="job_count" name="Jobs" radius={[0, 4, 4, 0]}>
                                {distribution.slice(0, 20).map((_, i) => (
                                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                )}
            </div>

            {/* Section 2: Key region comparison */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Radar chart */}
                <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                    <h2 className="text-sm font-semibold text-white mb-1">Skill Demand by Key Region</h2>
                    <p className="text-xs text-[#475569] mb-4">
                        Comparing Leicester · London · Nottingham · Leamington Spa
                    </p>
                    {compareLoading ? (
                        <div className="flex justify-center py-16">
                            <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
                        </div>
                    ) : radarData.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16 text-[#475569] text-sm">
                            <p>No comparison data available yet.</p>
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height={300}>
                            <RadarChart data={radarData}>
                                <PolarGrid stroke="#1e2d3d" />
                                <PolarAngleAxis dataKey="keyword" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                                <PolarRadiusAxis tick={{ fill: '#475569', fontSize: 9 }} />
                                {COMPARE_REGIONS.map((region, i) => (
                                    <Radar
                                        key={region}
                                        name={region}
                                        dataKey={region}
                                        stroke={COLORS[i]}
                                        fill={COLORS[i]}
                                        fillOpacity={0.12}
                                    />
                                ))}
                                <Tooltip content={<CustomTooltip />} />
                                <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 11 }}>{v}</span>} />
                            </RadarChart>
                        </ResponsiveContainer>
                    )}
                </div>

                {/* Per-region top skills table */}
                <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5">
                    <h2 className="text-sm font-semibold text-white mb-1">Top Skills per Region</h2>
                    <p className="text-xs text-[#475569] mb-4">Top 5 most demanded skills in each key region</p>
                    {compareLoading ? (
                        <div className="flex justify-center py-16">
                            <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
                        </div>
                    ) : (
                        <div className="space-y-4 overflow-y-auto max-h-72">
                            {COMPARE_REGIONS.map((region, ri) => {
                                const skills = (comparison[region] || []).slice(0, 5);
                                return (
                                    <div key={region}>
                                        <div className="flex items-center gap-2 mb-2">
                                            <span
                                                className="inline-block w-2.5 h-2.5 rounded-full"
                                                style={{ backgroundColor: COLORS[ri] }}
                                            />
                                            <span className="text-xs font-semibold text-white">{region}</span>
                                            {skills.length === 0 && (
                                                <span className="text-xs text-[#475569] ml-1">— no data yet</span>
                                            )}
                                        </div>
                                        {skills.length > 0 && (
                                            <div className="flex flex-wrap gap-1.5 pl-4">
                                                {skills.map(skill => (
                                                    <span
                                                        key={skill.keyword}
                                                        className="px-2 py-0.5 rounded-full text-xs border"
                                                        style={{
                                                            backgroundColor: `${COLORS[ri]}15`,
                                                            borderColor: `${COLORS[ri]}30`,
                                                            color: COLORS[ri],
                                                        }}
                                                    >
                                                        {skill.keyword}
                                                        <span className="opacity-60 ml-1">({skill.count})</span>
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>

            {/* Section 3: Full distribution table */}
            {distribution.length > 0 && (
                <div className="rounded-xl border border-[#1e2d3d] bg-[#0d1117] overflow-hidden">
                    <div className="p-5 border-b border-[#1e2d3d]">
                        <h2 className="text-sm font-semibold text-white">Full Regional Breakdown</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-[#1e2d3d]">
                                    <th className="text-left px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">#</th>
                                    <th className="text-left px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">Region</th>
                                    <th className="text-right px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">Job Listings</th>
                                    <th className="text-right px-5 py-3 text-xs font-medium text-[#475569] uppercase tracking-wider">Share</th>
                                </tr>
                            </thead>
                            <tbody>
                                {distribution.map((row, i) => {
                                    const total = distribution.reduce((s, r) => s + r.job_count, 0);
                                    const pct = total > 0 ? ((row.job_count / total) * 100).toFixed(1) : 0;
                                    return (
                                        <tr key={row.region} className="border-b border-[#0f1629] hover:bg-[#111827] transition-colors">
                                            <td className="px-5 py-3 text-[#475569]">{i + 1}</td>
                                            <td className="px-5 py-3 font-medium text-white flex items-center gap-2">
                                                <MapPin className="w-3.5 h-3.5 text-[#475569]" />
                                                {row.region}
                                            </td>
                                            <td className="px-5 py-3 text-right text-[#94a3b8]">{row.job_count}</td>
                                            <td className="px-5 py-3 text-right">
                                                <span className="text-xs text-[#64748b]">{pct}%</span>
                                                <div className="mt-1 h-1 rounded-full bg-[#1e2d3d] w-full">
                                                    <div
                                                        className="h-1 rounded-full bg-blue-500"
                                                        style={{ width: `${pct}%` }}
                                                    />
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Regional;
