import { useState, useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import api from '../lib/api';
import { Loader2, Users, Calendar, Link2 } from 'lucide-react';

export default function AdminDashboard() {
  const { activeCircle, adminCircles } = useApp();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const circle = activeCircle && adminCircles.find(c => c.id === activeCircle.id) ? activeCircle : adminCircles[0];

  useEffect(() => {
    if (!circle) { setLoading(false); return; }
    setLoading(true);
    Promise.all([
      api.get(`/circles/${circle.id}/members/`).catch(() => ({ data: { members: [] } })),
      api.get(`/circles/${circle.id}/events/`).catch(() => ({ data: { events: [] } })),
      api.get(`/circles/${circle.id}/invites/`).catch(() => ({ data: { invites: [] } })),
    ]).then(([m, e, i]) => {
      setStats({
        members: m.data.members?.length || 0,
        events: e.data.events?.length || 0,
        activeInvites: (i.data.invites || []).filter(inv => inv.is_active && !inv.used_at).length,
      });
    }).finally(() => setLoading(false));
  }, [circle]);

  if (!circle) {
    return (
      <div className="empty-state" data-testid="admin-no-circles">
        <Users className="h-10 w-10 text-gray-300" />
        <h2 className="text-lg font-medium text-black mt-4" style={{ fontFamily: 'Outfit' }}>No admin access</h2>
        <p className="empty-state-text">You are not an admin of any circle.</p>
      </div>
    );
  }

  return (
    <div data-testid="admin-dashboard">
      <p className="text-xs uppercase tracking-[0.2em] font-bold text-gray-400">{circle.name}</p>
      <h1 className="section-title mt-1">Admin Overview</h1>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : stats ? (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8">
          <div className="stat-card" data-testid="stat-members">
            <Users className="h-5 w-5 text-gray-400" />
            <p className="stat-value mt-2">{stats.members}</p>
            <p className="stat-label">Members</p>
          </div>
          <div className="stat-card" data-testid="stat-events">
            <Calendar className="h-5 w-5 text-gray-400" />
            <p className="stat-value mt-2">{stats.events}</p>
            <p className="stat-label">Events</p>
          </div>
          <div className="stat-card" data-testid="stat-invites">
            <Link2 className="h-5 w-5 text-gray-400" />
            <p className="stat-value mt-2">{stats.activeInvites}</p>
            <p className="stat-label">Active Invites</p>
          </div>
        </div>
      ) : null}
    </div>
  );
}
