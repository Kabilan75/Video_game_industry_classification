import React from 'react';

const StatsCard = ({ title, value, subtitle, icon: Icon, color = 'blue', trend }) => {
    const colors = {
        blue: { bg: 'from-blue-500/10 to-blue-600/5', border: 'border-blue-500/20', icon: 'text-blue-400', badge: 'bg-blue-500/10 text-blue-400' },
        purple: { bg: 'from-purple-500/10 to-purple-600/5', border: 'border-purple-500/20', icon: 'text-purple-400', badge: 'bg-purple-500/10 text-purple-400' },
        emerald: { bg: 'from-emerald-500/10 to-emerald-600/5', border: 'border-emerald-500/20', icon: 'text-emerald-400', badge: 'bg-emerald-500/10 text-emerald-400' },
        amber: { bg: 'from-amber-500/10 to-amber-600/5', border: 'border-amber-500/20', icon: 'text-amber-400', badge: 'bg-amber-500/10 text-amber-400' },
    };
    const c = colors[color];

    return (
        <div className={`relative rounded-xl border ${c.border} bg-gradient-to-br ${c.bg} p-5 card-hover overflow-hidden`}>
            {/* Background glow */}
            <div className={`absolute -top-4 -right-4 w-20 h-20 rounded-full opacity-20 blur-xl ${c.icon.replace('text-', 'bg-')}`} />

            <div className="flex items-start justify-between mb-3">
                <div className={`p-2 rounded-lg ${c.badge}`}>
                    <Icon className={`w-4 h-4 ${c.icon}`} />
                </div>
                {trend !== undefined && (
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${trend >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                        {trend >= 0 ? '+' : ''}{trend}%
                    </span>
                )}
            </div>

            <div className="text-2xl font-bold text-white mb-0.5">{value}</div>
            <div className="text-sm font-medium text-[#94a3b8]">{title}</div>
            {subtitle && <div className="text-xs text-[#475569] mt-1">{subtitle}</div>}
        </div>
    );
};

export default StatsCard;
