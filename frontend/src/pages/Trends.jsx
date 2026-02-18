import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts';
import { getTopKeywords } from '../api/client';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1', '#14b8a6', '#f97316'];

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

const Trends = () => {
    const [keywords, setKeywords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeCategory, setActiveCategory] = useState(null);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const params = { limit: 20 };
                if (activeCategory) params.category = activeCategory;
                const data = await getTopKeywords(params);
                setKeywords(data.keywords || []);
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

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">
                    Keyword <span className="gradient-text">Trends</span>
                </h1>
                <p className="text-[#64748b] text-sm mt-1">Most in-demand skills across UK games industry jobs</p>
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
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="45%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={3}
                                    dataKey="value"
                                >
                                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                                <Legend
                                    formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 11 }}>{value}</span>}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Table */}
                    <div className="xl:col-span-3 rounded-xl border border-[#1e2d3d] bg-[#0d1117] overflow-hidden">
                        <div className="p-5 border-b border-[#1e2d3d]">
                            <h2 className="text-sm font-semibold text-white">Full Keyword Rankings</h2>
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
