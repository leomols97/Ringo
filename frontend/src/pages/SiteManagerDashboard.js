import { useState, useEffect, useCallback } from 'react';
import api from '../lib/api';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Button } from '../components/ui/button';
import Pagination from '../components/Pagination';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '../components/ui/dialog';
import { Loader2, Users, CircleDot, Calendar, Clock, Search, Pencil } from 'lucide-react';
import { toast } from '../components/ui/sonner';

export default function SiteManagerDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [userPagination, setUserPagination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userSearch, setUserSearch] = useState('');
  const [userPage, setUserPage] = useState(1);
  const [showUsers, setShowUsers] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [editSaving, setEditSaving] = useState(false);

  useEffect(() => {
    api.get('/admin/overview/').then(r => setStats(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const fetchUsers = useCallback(async () => {
    if (!showUsers) return;
    const params = new URLSearchParams();
    if (userSearch) params.set('search', userSearch);
    params.set('page', userPage);
    params.set('per_page', 20);
    try {
      const r = await api.get(`/admin/users/?${params}`);
      setUsers(r.data.users || []);
      setUserPagination(r.data.pagination || null);
    } catch { setUsers([]); }
  }, [showUsers, userSearch, userPage]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const openEdit = async (uid) => {
    try {
      const r = await api.get(`/admin/users/${uid}/`);
      const u = r.data;
      setEditForm({ first_name: u.first_name, last_name: u.last_name, phone: u.phone, is_active: u.is_active });
      setEditUser(u);
    } catch { toast.error('Failed to load user'); }
  };

  const handleEditSave = async () => {
    setEditSaving(true);
    try {
      await api.patch(`/admin/users/${editUser.id}/`, editForm);
      setEditUser(null);
      fetchUsers();
      toast.success('User updated');
    } catch (e) { toast.error(e.response?.data?.error || 'Failed to update'); }
    finally { setEditSaving(false); }
  };

  return (
    <div data-testid="site-manager-dashboard">
      <h1 className="section-title">Site Overview</h1>
      <p className="section-subtitle">Platform-wide statistics</p>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : stats ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8">
            <div className="stat-card"><Users className="h-5 w-5 text-gray-400" /><p className="stat-value mt-2">{stats.users_count}</p><p className="stat-label">Users</p></div>
            <div className="stat-card"><CircleDot className="h-5 w-5 text-gray-400" /><p className="stat-value mt-2">{stats.circles_count}</p><p className="stat-label">Circles</p></div>
            <div className="stat-card"><Calendar className="h-5 w-5 text-gray-400" /><p className="stat-value mt-2">{stats.events_count}</p><p className="stat-label">Events</p></div>
            <div className="stat-card"><Clock className="h-5 w-5 text-gray-400" /><p className="stat-value mt-2">{stats.pending_signups_count}</p><p className="stat-label">Pending</p></div>
          </div>

          <div className="mt-10">
            <button onClick={() => { setShowUsers(p => !p); setUserPage(1); }} className="text-sm font-medium text-black hover:underline" data-testid="toggle-users-btn">
              {showUsers ? 'Hide users' : 'Manage users'}
            </button>
            {showUsers && (
              <div className="mt-4 animate-fade-in">
                <div className="relative max-w-xs mb-4">
                  <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                  <Input placeholder="Search users..." value={userSearch} onChange={e => { setUserSearch(e.target.value); setUserPage(1); }} className="pl-8 rounded-sm text-xs h-8" data-testid="users-search" />
                </div>
                <div className="border-t border-gray-200">
                  {users.map(u => (
                    <div key={u.id} className="data-row px-1" data-testid={`user-row-${u.id}`}>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-black">{u.first_name} {u.last_name}</p>
                        <p className="text-xs text-gray-400">{u.email}{u.phone ? ` · ${u.phone}` : ''}</p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {u.is_site_manager && <span className="text-xs px-2 py-0.5 rounded-sm border text-blue-700 border-blue-200 bg-blue-50">Manager</span>}
                        <span className={`text-xs px-2 py-0.5 rounded-sm border ${u.is_active ? 'text-green-700 border-green-200' : 'text-red-600 border-red-200'}`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => openEdit(u.id)} data-testid={`edit-user-${u.id}`} aria-label="Edit user">
                          <Pencil className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  {users.length === 0 && <p className="text-xs text-gray-400 py-4 text-center">No users found</p>}
                </div>
                <Pagination pagination={userPagination} onPageChange={setUserPage} />
              </div>
            )}
          </div>

          {/* Edit user dialog */}
          <Dialog open={!!editUser} onOpenChange={(open) => { if (!open) setEditUser(null); }}>
            <DialogContent className="rounded-sm max-w-sm">
              <DialogHeader><DialogTitle style={{ fontFamily: 'Outfit' }}>Edit User</DialogTitle></DialogHeader>
              {editUser && (
                <div className="space-y-3 py-2">
                  <p className="text-xs text-gray-400">{editUser.email}</p>
                  <div>
                    <Label className="text-xs uppercase tracking-wider text-gray-500">First name</Label>
                    <Input value={editForm.first_name || ''} onChange={e => setEditForm(p => ({ ...p, first_name: e.target.value }))} className="mt-1 rounded-sm" data-testid="edit-user-first-name" />
                  </div>
                  <div>
                    <Label className="text-xs uppercase tracking-wider text-gray-500">Last name</Label>
                    <Input value={editForm.last_name || ''} onChange={e => setEditForm(p => ({ ...p, last_name: e.target.value }))} className="mt-1 rounded-sm" data-testid="edit-user-last-name" />
                  </div>
                  <div>
                    <Label className="text-xs uppercase tracking-wider text-gray-500">Phone</Label>
                    <Input value={editForm.phone || ''} onChange={e => setEditForm(p => ({ ...p, phone: e.target.value }))} className="mt-1 rounded-sm" data-testid="edit-user-phone" />
                  </div>
                  <div className="flex items-center gap-2">
                    <input type="checkbox" checked={editForm.is_active} onChange={e => setEditForm(p => ({ ...p, is_active: e.target.checked }))} id="user-active" data-testid="edit-user-active" />
                    <Label htmlFor="user-active" className="text-xs text-gray-500">Active</Label>
                  </div>
                </div>
              )}
              <DialogFooter>
                <Button onClick={handleEditSave} className="rounded-sm bg-black text-white hover:bg-gray-800" disabled={editSaving} data-testid="edit-user-save">
                  {editSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </>
      ) : (
        <div className="empty-state"><p className="empty-state-text">Failed to load overview.</p></div>
      )}
    </div>
  );
}
