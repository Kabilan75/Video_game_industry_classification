import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Menu } from 'lucide-react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Trends from './pages/Trends';
import Regional from './pages/Regional';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="flex min-h-screen bg-[#0a0e1a] text-slate-300 font-sans">
        {/* Mobile Header */}
        <header className="md:hidden fixed top-0 w-full z-40 bg-[#0d1117] border-b border-[#1e2d3d] px-4 py-3 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold text-xs">UK</span>
            </div>
            <span className="font-bold text-white tracking-wide">Games Industry</span>
          </div>
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg bg-[#1e2d3d] text-white hover:bg-[#334155] transition-colors"
            aria-label="Open Menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        </header>

        {/* Sidebar (with Mobile Overlay logic passed down) */}
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        {/* Main Content Area */}
        <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'blur-sm md:blur-none' : ''} md:ml-64 p-4 pt-20 md:p-8 md:pt-8 overflow-y-auto`}>
          <div className="max-w-7xl mx-auto space-y-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/jobs" element={<Jobs />} />
              <Route path="/trends" element={<Trends />} />
              <Route path="/regional" element={<Regional />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
