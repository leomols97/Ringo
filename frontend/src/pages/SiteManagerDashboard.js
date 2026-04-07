import { useState, useEffect } from 'react';
import api from '../lib/api';
import { Loader2, Users, CircleDot, Calendar, Clock } from 'lucide-react';

export default function SiteManagerDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/admin/overview/').then(r => setStats(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div data-testid="site-manager-dashboard">
      <h1 className="section-title">Site Overview</h1>
      <p className="section-subtitle">Platform-wide statistics</p>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : stats ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8">
          <div className="stat-card" data-testid="stat-users">
            <Users className="h-5 w-5 text-gray-400" />
            <p className="stat-value mt-2">{stats.users_count}</p>
            <p className="stat-label">Users</p>
          </div>
          <div className="stat-card" data-testid="stat-circles">
            <CircleDot className="h-5 w-5 text-gray-400" />
            <p className="stat-value mt-2">{stats.circles_count}</p>
            <p className="stat-label">Circles</p>
          </div>
          <div className="stat-card" data-testid="stat-events">
            <Calendar className="h-5 w-5 text-gray-400" />
            <p className="stat-value mt-2">{stats.events_count}</p>
            <p className="stat-label">Events</p>
          </div>
          <div className="stat-card" data-testid="stat-pending">
            <Clock className="h-5 w-5 text-gray-400" />
            <p className="stat-value mt-2">{stats.pending_signups_count}</p>
            <p className="stat-label">Pending</p>
          </div>
        </div>
      ) : (
        <div className="empty-state"><p className="empty-state-text">Failed to load overview data.</p></div>
      )}
    </div>
  );
}
