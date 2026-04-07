import { useState, useEffect } from 'react';
import api from '../lib/api';
import { Input } from '../components/ui/input';
import { Loader2, Users, CircleDot, Calendar, Clock, Search } from 'lucide-react';

export default function SiteManagerDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userSearch, setUserSearch] = useState('');
  const [showUsers, setShowUsers] = useState(false);

  useEffect(() => {
    api.get('/admin/overview/').then(r => setStats(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!showUsers) return;
    const params = userSearch ? `?search=${encodeURIComponent(userSearch)}` : '';
    api.get(`/admin/users/${params}`).then(r => setUsers(r.data.users || [])).catch(() => setUsers([]));
  }, [showUsers, userSearch]);

  return (
    <div data-testid="site-manager-dashboard">
      <h1 className="section-title">Site Overview</h1>
      <p className="section-subtitle">Platform-wide statistics</p>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : stats ? (
        <>
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

          {/* Users section */}
          <div className="mt-10">
            <button
              onClick={() => setShowUsers(p => !p)}
              className="text-sm font-medium text-black hover:underline"
              data-testid="toggle-users-btn"
            >
              {showUsers ? 'Hide users' : 'Show all users'}
            </button>
            {showUsers && (
              <div className="mt-4 animate-fade-in">
                <div className="relative max-w-xs mb-4">
                  <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                  <Input
                    placeholder="Search users..."
                    value={userSearch}
                    onChange={e => setUserSearch(e.target.value)}
                    className="pl-8 rounded-sm text-xs h-8"
                    data-testid="users-search"
                  />
                </div>
                <div className="border-t border-gray-200">
                  {users.map(u => (
                    <div key={u.id} className="data-row px-1" data-testid={`user-row-${u.id}`}>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-black">{u.first_name} {u.last_name}</p>
                        <p className="text-xs text-gray-400">{u.email}</p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {u.is_site_manager && <span className="text-xs px-2 py-0.5 rounded-sm border text-blue-700 border-blue-200 bg-blue-50">Site Manager</span>}
                        <span className={`text-xs px-2 py-0.5 rounded-sm border ${u.is_active ? 'text-green-700 border-green-200' : 'text-red-600 border-red-200'}`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                  ))}
                  {users.length === 0 && <p className="text-xs text-gray-400 py-4 text-center">No users found</p>}
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="empty-state"><p className="empty-state-text">Failed to load overview data.</p></div>
      )}
    </div>
  );
}
