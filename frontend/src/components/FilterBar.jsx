import React from 'react';
import { Search, SlidersHorizontal } from 'lucide-react';

const FilterBar = ({ filters, onFilterChange }) => {
    const handleChange = (e) => {
        const { name, value } = e.target;
        onFilterChange({ ...filters, [name]: value });
    };

    const inputClass =
        'w-full px-3 py-2 text-sm bg-[#0d1117] border border-[#1e2d3d] rounded-lg text-[#e2e8f0] placeholder-[#475569] focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all';

    return (
        <div className="flex flex-wrap items-center gap-3 p-4 rounded-xl border border-[#1e2d3d] bg-[#0d1117]">
            <SlidersHorizontal className="w-4 h-4 text-[#475569] flex-shrink-0" />

            <div className="relative flex-1 min-w-[180px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#475569]" />
                <input
                    type="text"
                    name="keyword"
                    placeholder="Search title or skill..."
                    value={filters.keyword || ''}
                    onChange={handleChange}
                    className={`${inputClass} pl-9`}
                />
            </div>

            <input
                type="text"
                name="location"
                placeholder="Location (e.g. London)"
                value={filters.location || ''}
                onChange={handleChange}
                className={`${inputClass} flex-1 min-w-[150px]`}
            />

            <input
                type="text"
                name="company"
                placeholder="Company"
                value={filters.company || ''}
                onChange={handleChange}
                className={`${inputClass} flex-1 min-w-[140px]`}
            />

            {(filters.keyword || filters.location || filters.company) && (
                <button
                    onClick={() => onFilterChange({ keyword: '', location: '', company: '' })}
                    className="text-xs text-[#64748b] hover:text-white px-3 py-2 rounded-lg border border-[#1e2d3d] hover:border-[#334155] transition-all"
                >
                    Clear
                </button>
            )}
        </div>
    );
};

export default FilterBar;
