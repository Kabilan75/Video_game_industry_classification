import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Trends from './pages/Trends';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-[#0a0e1a]">
        <Sidebar />
        <main className="flex-1 ml-64 p-8 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/trends" element={<Trends />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
