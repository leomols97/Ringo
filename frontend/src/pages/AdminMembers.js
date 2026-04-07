import { useState, useEffect, useCallback } from 'react';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import Pagination from '../components/Pagination';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { Loader2, Users, ShieldCheck, ShieldMinus, UserMinus, Search } from 'lucide-react';
import { toast } from '../components/ui/sonner';

export default function AdminMembers() {
  const { user } = useAuth();
  const { activeCircle, adminCircles } = useApp();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('joined_at');
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);

  const circle = activeCircle && (user?.is_site_manager || adminCircles.find(c => c.id === activeCircle.id))
    ? activeCircle
    : adminCircles[0] || null;

  const fetchMembers = useCallback(async () => {
    if (!circle) return;
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set('search', search);
      if (sort) params.set('sort', sort);
      params.set('page', page);
      const r = await api.get(`/circles/${circle.id}/members/?${params}`);
      setMembers(r.data.members || []);
      setPagination(r.data.pagination || null);
    } catch { setMembers([]); }
    finally { setLoading(false); }
  }, [circle, search, sort, page]);

  useEffect(() => { fetchMembers(); }, [fetchMembers]);

  const handleAction = async (action, mid) => {
    setError('');
    try {
      await api.post(`/circles/${circle.id}/members/${mid}/${action}/`);
      fetchMembers();
      const labels = { promote: 'Promoted', demote: 'Demoted', remove: 'Removed' };
      toast.success(labels[action] || 'Done');
    } catch (e) {
      const msg = e.response?.data?.error || `Failed to ${action} member`;
      setError(msg);
      toast.error(msg);
    }
  };

  if (!circle) return <div className="empty-state"><Users className="h-10 w-10 text-gray-300" /><p className="empty-state-text mt-3">Select an admin circle first.</p></div>;

  return (
    <div data-testid="admin-members-page">
      <p className="text-xs uppercase tracking-[0.2em] font-bold text-gray-400">{circle.name}</p>
      <h1 className="section-title mt-1">Members</h1>

      <div className="flex items-center gap-3 mt-4">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
          <Input
            placeholder="Search members..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-8 rounded-sm text-xs h-8"
            data-testid="members-search"
          />
        </div>
        <select
          value={sort}
          onChange={e => setSort(e.target.value)}
          className="text-xs border border-gray-200 rounded-sm px-2 h-8 bg-white"
          data-testid="members-sort"
          aria-label="Sort members by"
        >
          <option value="joined_at">Joined date</option>
          <option value="name">Name</option>
          <option value="role">Role</option>
        </select>
      </div>

      {error && <div className="mt-3 p-2.5 text-xs text-red-600 border border-red-200 rounded-sm bg-red-50" data-testid="members-error">{error}</div>}

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : members.length === 0 ? (
        <div className="empty-state"><Users className="h-8 w-8 text-gray-300" /><p className="empty-state-text mt-3">{search ? 'No matching members' : 'No members'}</p></div>
      ) : (
        <div className="mt-4 border-t border-gray-200">
          {members.map(m => (
            <div key={m.id} className="data-row px-1" data-testid={`member-row-${m.id}`}>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-black">{m.user_first_name} {m.user_last_name}</p>
                <p className="text-xs text-gray-400">{m.user_email}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`text-xs px-2 py-0.5 rounded-sm border ${m.role === 'CIRCLE_ADMIN' ? 'text-blue-700 border-blue-200 bg-blue-50' : 'text-gray-500 border-gray-200'}`}>
                  {m.role === 'CIRCLE_ADMIN' ? 'Admin' : 'Member'}
                </span>
                {m.role === 'MEMBER' ? (
                  <Button variant="ghost" size="sm" className="text-xs h-7 px-2" onClick={() => handleAction('promote', m.id)} data-testid={`promote-${m.id}`} aria-label={`Promote ${m.user_first_name}`}>
                    <ShieldCheck className="h-3.5 w-3.5" />
                  </Button>
                ) : (
                  <Button variant="ghost" size="sm" className="text-xs h-7 px-2" onClick={() => handleAction('demote', m.id)} data-testid={`demote-${m.id}`} aria-label={`Demote ${m.user_first_name}`}>
                    <ShieldMinus className="h-3.5 w-3.5" />
                  </Button>
                )}
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-xs h-7 px-2 text-red-600 hover:text-red-700" data-testid={`remove-trigger-${m.id}`} aria-label={`Remove ${m.user_first_name}`}>
                      <UserMinus className="h-3.5 w-3.5" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent className="rounded-sm">
                    <AlertDialogHeader>
                      <AlertDialogTitle>Remove member?</AlertDialogTitle>
                      <AlertDialogDescription>Remove {m.user_first_name} from {circle.name}?</AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel className="rounded-sm">Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleAction('remove', m.id)} className="rounded-sm bg-red-600 hover:bg-red-700" data-testid={`remove-confirm-${m.id}`}>
                        Remove
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          ))}
          <Pagination pagination={pagination} onPageChange={setPage} />
        </div>
      )}
    </div>
  );
}
