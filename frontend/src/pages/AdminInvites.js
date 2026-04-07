import { useState, useEffect, useCallback } from 'react';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import { Loader2, Link2, Copy, Check, Ban } from 'lucide-react';

export default function AdminInvites() {
  const { user } = useAuth();
  const { activeCircle, adminCircles } = useApp();
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [copiedId, setCopiedId] = useState(null);

  const circle = activeCircle && (user?.is_site_manager || adminCircles.find(c => c.id === activeCircle.id))
    ? activeCircle
    : adminCircles[0] || null;

  const fetchInvites = useCallback(async () => {
    if (!circle) return;
    setLoading(true);
    try {
      const r = await api.get(`/circles/${circle.id}/invites/`);
      setInvites(r.data.invites || []);
    } catch { setInvites([]); }
    finally { setLoading(false); }
  }, [circle]);

  useEffect(() => { fetchInvites(); }, [fetchInvites]);

  const createInvite = async () => {
    setCreating(true);
    try {
      await api.post(`/circles/${circle.id}/invites/`);
      await fetchInvites();
    } catch {}
    finally { setCreating(false); }
  };

  const deactivate = async (iid) => {
    await api.post(`/circles/${circle.id}/invites/${iid}/deactivate/`);
    fetchInvites();
  };

  const copyLink = (token, id) => {
    const url = `${window.location.origin}/invite/${token}`;
    navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const isExpired = (expiresAt) => new Date(expiresAt) < new Date();
  const isUsable = (inv) => inv.is_active && !inv.used_at && !isExpired(inv.expires_at);

  if (!circle) return <div className="empty-state"><Link2 className="h-10 w-10 text-gray-300" /><p className="empty-state-text mt-3">Select an admin circle.</p></div>;

  return (
    <div data-testid="admin-invites-page">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] font-bold text-gray-400">{circle.name}</p>
          <h1 className="section-title mt-1">Invitations</h1>
        </div>
        <Button onClick={createInvite} className="rounded-sm bg-black text-white hover:bg-gray-800" disabled={creating} data-testid="create-invite-btn">
          {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Generate link'}
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : invites.length === 0 ? (
        <div className="empty-state"><Link2 className="h-8 w-8 text-gray-300" /><p className="empty-state-text mt-3">No invitations yet</p></div>
      ) : (
        <div className="mt-6 border-t border-gray-200">
          {invites.map(inv => (
            <div key={inv.id} className="data-row px-1" data-testid={`invite-row-${inv.id}`}>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-mono text-gray-600 truncate">{inv.token}</p>
                <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
                  <span>Expires {new Date(inv.expires_at).toLocaleDateString()}</span>
                  {inv.used_at && <span>Used {new Date(inv.used_at).toLocaleDateString()}</span>}
                </div>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <span className={`text-xs px-2 py-0.5 rounded-sm border ${
                  isUsable(inv) ? 'text-green-700 border-green-200 bg-green-50' :
                  inv.used_at ? 'text-gray-500 border-gray-200' :
                  'text-red-600 border-red-200 bg-red-50'
                }`}>
                  {isUsable(inv) ? 'Active' : inv.used_at ? 'Used' : isExpired(inv.expires_at) ? 'Expired' : 'Inactive'}
                </span>
                {isUsable(inv) && (
                  <>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => copyLink(inv.token, inv.id)} data-testid={`copy-invite-${inv.id}`}>
                      {copiedId === inv.id ? <Check className="h-3.5 w-3.5 text-green-600" /> : <Copy className="h-3.5 w-3.5" />}
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-red-600 hover:text-red-700" onClick={() => deactivate(inv.id)} data-testid={`deactivate-invite-${inv.id}`}>
                      <Ban className="h-3.5 w-3.5" />
                    </Button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
