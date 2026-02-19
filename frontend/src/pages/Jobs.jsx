import React, { useState, useEffect, useCallback } from 'react';
import { Loader2, ChevronLeft, ChevronRight, Download, Printer } from 'lucide-react';
import JobCard from '../components/JobCard';
import FilterBar from '../components/FilterBar';
import { getJobs, buildExportUrl } from '../api/client';

const Jobs = () => {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({ keyword: '', location: 'London', company: '' });
    const [page, setPage] = useState(1);
    const [meta, setMeta] = useState({ total: 0, total_pages: 1 });

    const fetchJobs = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const params = { page, page_size: 20 };
            if (filters.keyword) params.keyword = filters.keyword;
            if (filters.location) params.location = filters.location;
            if (filters.company) params.company = filters.company;
            const data = await getJobs(params);
            setJobs(data.items);
            setMeta({ total: data.total, total_pages: data.total_pages });
        } catch {
            setError('Failed to load jobs. Is the backend running?');
        } finally {
            setLoading(false);
        }
    }, [page, filters]);

    useEffect(() => { fetchJobs(); }, [fetchJobs]);

    const handleFilterChange = (f) => { setFilters(f); setPage(1); };

    const exportParams = {};
    if (filters.keyword) exportParams.keyword = filters.keyword;
    if (filters.location) exportParams.location = filters.location;
    if (filters.company) exportParams.company = filters.company;

    return (
        <div className="space-y-5">
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">
                        UK <span className="gradient-text">Job Listings</span>
                    </h1>
                    <p className="text-[#64748b] text-sm mt-1">
                        {meta.total} active UK games industry positions
                    </p>
                </div>
                {/* Export & Print */}
                <div className="flex gap-2">
                    <a
                        href={buildExportUrl('jobs', exportParams)}
                        download
                        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[#0d1117] border border-[#1e2d3d] text-sm text-[#94a3b8] hover:text-white hover:border-[#334155] transition-all"
                        title="Download current filter as CSV"
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

            <FilterBar filters={filters} onFilterChange={handleFilterChange} />

            {error && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="flex justify-center py-20">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                </div>
            ) : jobs.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 text-[#475569]">
                    <p className="text-lg font-medium">No jobs found</p>
                    <p className="text-sm mt-1">Try adjusting your filters</p>
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-1 gap-3 print-area">
                        {jobs.map(job => <JobCard key={job.id} job={job} />)}
                    </div>

                    {/* Pagination — hidden when printing */}
                    <div className="flex items-center justify-between pt-2 no-print">
                        <p className="text-sm text-[#475569]">
                            Page {page} of {meta.total_pages}
                        </p>
                        <div className="flex gap-2">
                            <button
                                disabled={page <= 1}
                                onClick={() => setPage(p => p - 1)}
                                className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-[#1e2d3d] text-[#94a3b8] hover:text-white hover:border-[#334155] disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                            >
                                <ChevronLeft className="w-4 h-4" /> Prev
                            </button>
                            <button
                                disabled={page >= meta.total_pages}
                                onClick={() => setPage(p => p + 1)}
                                className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-[#1e2d3d] text-[#94a3b8] hover:text-white hover:border-[#334155] disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                            >
                                Next <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default Jobs;
