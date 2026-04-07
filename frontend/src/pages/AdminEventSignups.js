import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import { Loader2, ArrowLeft, CheckCircle, XCircle } from 'lucide-react';

export default function AdminEventSignups() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadSignups = async () => {
    try {
      const r = await api.get(`/events/${id}/signups/`);
      setData(r.data);
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { loadSignups(); }, [id]);

  const approve = async (sid) => { await api.post(`/signups/${sid}/approve/`); loadSignups(); };
  const reject = async (sid) => { await api.post(`/signups/${sid}/reject/`); loadSignups(); };

  if (loading) return <div className="flex justify-center py-16"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>;

  return (
    <div data-testid="admin-event-signups-page">
      <button onClick={() => navigate('/admin/events')} className="flex items-center gap-1 text-xs text-gray-400 hover:text-black transition-colors mb-6" data-testid="back-btn">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to events
      </button>

      <h1 className="section-title">{data?.event?.title || 'Event'} - Signups</h1>

      {(!data?.signups || data.signups.length === 0) ? (
        <div className="empty-state"><p className="empty-state-text">No signup requests yet.</p></div>
      ) : (
        <div className="mt-6 border-t border-gray-200">
          {data.signups.map(s => (
            <div key={s.id} className="data-row px-1" data-testid={`signup-row-${s.id}`}>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-black">{s.user_first_name} {s.user_last_name}</p>
                <p className="text-xs text-gray-400">{s.user_email} &middot; {new Date(s.requested_at).toLocaleDateString()}</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`text-xs px-2 py-0.5 rounded-sm border ${
                  s.status === 'APPROVED' ? 'text-green-700 border-green-200 bg-green-50' :
                  s.status === 'PENDING' ? 'text-amber-700 border-amber-200 bg-amber-50' :
                  'text-red-700 border-red-200 bg-red-50'
                }`}>{s.status}</span>
                {s.status === 'PENDING' && (
                  <>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-green-600" onClick={() => approve(s.id)} data-testid={`approve-${s.id}`}>
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-red-600" onClick={() => reject(s.id)} data-testid={`reject-${s.id}`}>
                      <XCircle className="h-4 w-4" />
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
