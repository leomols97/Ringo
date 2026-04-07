import { useState, useEffect, useCallback } from 'react';
import { useApp } from '../contexts/AppContext';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { Loader2, Users, ShieldCheck, ShieldMinus, UserMinus } from 'lucide-react';

export default function AdminMembers() {
  const { activeCircle, adminCircles } = useApp();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  const circle = activeCircle && adminCircles.find(c => c.id === activeCircle.id) ? activeCircle : adminCircles[0];

  const fetchMembers = useCallback(async () => {
    if (!circle) return;
    setLoading(true);
    try {
      const r = await api.get(`/circles/${circle.id}/members/`);
      setMembers(r.data.members || []);
    } catch { setMembers([]); }
    finally { setLoading(false); }
  }, [circle]);

  useEffect(() => { fetchMembers(); }, [fetchMembers]);

  const promote = async (mid) => { await api.post(`/circles/${circle.id}/members/${mid}/promote/`); fetchMembers(); };
  const demote = async (mid) => { await api.post(`/circles/${circle.id}/members/${mid}/demote/`); fetchMembers(); };
  const remove = async (mid) => { await api.post(`/circles/${circle.id}/members/${mid}/remove/`); fetchMembers(); };

  if (!circle) return <div className="empty-state"><Users className="h-10 w-10 text-gray-300" /><p className="empty-state-text mt-3">Select an admin circle first.</p></div>;

  return (
    <div data-testid="admin-members-page">
      <p className="text-xs uppercase tracking-[0.2em] font-bold text-gray-400">{circle.name}</p>
      <h1 className="section-title mt-1">Members</h1>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : members.length === 0 ? (
        <div className="empty-state"><Users className="h-8 w-8 text-gray-300" /><p className="empty-state-text mt-3">No members</p></div>
      ) : (
        <div className="mt-6 border-t border-gray-200">
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
                  <Button variant="ghost" size="sm" className="text-xs h-7 px-2" onClick={() => promote(m.id)} data-testid={`promote-${m.id}`}>
                    <ShieldCheck className="h-3.5 w-3.5" />
                  </Button>
                ) : (
                  <Button variant="ghost" size="sm" className="text-xs h-7 px-2" onClick={() => demote(m.id)} data-testid={`demote-${m.id}`}>
                    <ShieldMinus className="h-3.5 w-3.5" />
                  </Button>
                )}
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="ghost" size="sm" className="text-xs h-7 px-2 text-red-600 hover:text-red-700" data-testid={`remove-trigger-${m.id}`}>
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
                      <AlertDialogAction onClick={() => remove(m.id)} className="rounded-sm bg-red-600 hover:bg-red-700" data-testid={`remove-confirm-${m.id}`}>
                        Remove
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
