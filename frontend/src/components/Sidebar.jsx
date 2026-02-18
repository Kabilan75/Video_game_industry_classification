import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, TrendingUp, MapPin, Gamepad2 } from 'lucide-react';

const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/jobs', icon: Briefcase, label: 'Jobs' },
    { to: '/trends', icon: TrendingUp, label: 'Trends' },
    { to: '/regional', icon: MapPin, label: 'Regional' },
];

const Sidebar = () => (
    <aside className="fixed left-0 top-0 h-full w-64 bg-[#0d1117] border-r border-[#1e2d3d] flex flex-col z-50">
        {/* Logo */}
        <div className="px-6 py-6 border-b border-[#1e2d3d]">
            <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <Gamepad2 className="w-5 h-5 text-white" />
                </div>
                <div>
                    <p className="text-white font-bold text-sm leading-tight">UK Games</p>
                    <p className="text-[#64748b] text-xs">Industry Dashboard</p>
                </div>
            </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
            {navItems.map(({ to, icon: Icon, label }) => (
                <NavLink
                    key={to}
                    to={to}
                    end={to === '/'}
                    className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${isActive
                            ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                            : 'text-[#94a3b8] hover:text-white hover:bg-[#1e2d3d]'
                        }`
                    }
                >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    {label}
                </NavLink>
            ))}
        </nav>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-[#1e2d3d]">
            <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-slow" />
                <span className="text-xs text-[#64748b]">Live data</span>
            </div>
            <p className="text-xs text-[#334155] mt-1">Leicester Games Network</p>
        </div>
    </aside>
);

export default Sidebar;
