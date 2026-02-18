import React from 'react';
import { MapPin, Building2, Calendar, ExternalLink, Banknote, Tag } from 'lucide-react';

const categoryColors = {
    skills: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    software: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    experience: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
};

const JobCard = ({ job }) => {
    const formatDate = (d) => {
        if (!d) return 'Recently';
        return new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    };

    return (
        <div className="group relative rounded-xl border border-[#1e2d3d] bg-[#0d1117] p-5 card-hover hover:border-blue-500/30 transition-all duration-200">
            {/* Subtle top gradient line */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-t-xl" />

            <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold text-white group-hover:text-blue-400 transition-colors truncate">
                        {job.title}
                    </h3>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5 text-sm text-[#64748b]">
                        <span className="flex items-center gap-1">
                            <Building2 className="w-3.5 h-3.5 flex-shrink-0" />
                            {job.company}
                        </span>
                        <span className="flex items-center gap-1">
                            <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
                            {job.location || 'UK'}
                        </span>
                        {job.salary && (
                            <span className="flex items-center gap-1 text-emerald-400">
                                <Banknote className="w-3.5 h-3.5 flex-shrink-0" />
                                {job.salary}
                            </span>
                        )}
                    </div>
                </div>

                <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-shrink-0 p-2 rounded-lg bg-[#1e2d3d] hover:bg-blue-600 text-[#64748b] hover:text-white transition-all duration-150"
                    title="View job"
                >
                    <ExternalLink className="w-4 h-4" />
                </a>
            </div>

            <div className="flex items-center justify-between mt-4 pt-3 border-t border-[#1e2d3d]">
                <div className="flex items-center gap-1.5 text-xs text-[#475569]">
                    <Calendar className="w-3.5 h-3.5" />
                    {formatDate(job.posting_date)}
                </div>
                <span className="text-xs px-2 py-0.5 rounded-full bg-[#1e2d3d] text-[#64748b] border border-[#1e2d3d]">
                    {job.source_website}
                </span>
            </div>
        </div>
    );
};

export default JobCard;
