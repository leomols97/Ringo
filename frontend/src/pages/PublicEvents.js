import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import Pagination from '../components/Pagination';
import { Calendar, MapPin, Clock, Loader2, Globe } from 'lucide-react';
import { toast } from '../components/ui/sonner';
import { Button } from '../components/ui/button';

const fmt = (iso) => new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
const fmtTime = (iso) => new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

export default function PublicEvents() {
  const [events, setEvents] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    try {
      const r = await api.get(`/events/public/?page=${page}&per_page=20`);
      setEvents(r.data.events || []);
      setPagination(r.data.pagination || null);
    } catch { setEvents([]); }
    finally { setLoading(false); }
  }, [page]);

  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  const handleSignup = async (eid) => {
    try {
      await api.post(`/events/${eid}/signup/`);
      toast.success('Signup request sent');
      fetchEvents();
    } catch (e) {
      toast.error(e.response?.data?.error || 'Signup failed');
    }
  };

  return (
    <div data-testid="public-events-page">
      <div className="flex items-center gap-2 mb-6">
        <Globe className="h-5 w-5 text-blue-500" />
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-black" style={{ fontFamily: 'Outfit' }}>Public Events</h1>
      </div>
      <p className="text-sm text-gray-500 mb-6">Open events from all circles — no membership required to join.</p>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : events.length === 0 ? (
        <div className="empty-state">
          <Globe className="h-8 w-8 text-gray-300" />
          <p className="empty-state-text mt-3">No public events right now.</p>
        </div>
      ) : (
        <div className="border-t border-gray-200">
          {events.map(e => (
            <div key={e.id} className="data-row px-1" data-testid={`public-event-${e.id}`}>
              <Link to={`/events/${e.id}`} className="flex-1 min-w-0 block">
                <p className="text-sm font-medium text-black truncate">{e.title}</p>
                <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
                  <span>{e.circle_name}</span>
                  <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{fmt(e.start_datetime)}</span>
                  <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{fmtTime(e.start_datetime)}</span>
                  {e.location && <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{e.location}</span>}
                </div>
              </Link>
              <div className="shrink-0 ml-2">
                {e.my_signup_status ? (
                  <span className={`text-xs px-2 py-0.5 rounded-sm border ${
                    e.my_signup_status === 'APPROVED' ? 'text-green-700 border-green-200 bg-green-50' :
                    e.my_signup_status === 'PENDING' ? 'text-amber-700 border-amber-200 bg-amber-50' :
                    'text-red-700 border-red-200 bg-red-50'
                  }`}>{e.my_signup_status}</span>
                ) : (
                  <Button size="sm" className="rounded-sm bg-black text-white hover:bg-gray-800 text-xs h-7" onClick={() => handleSignup(e.id)} data-testid={`signup-public-${e.id}`}>
                    Join
                  </Button>
                )}
              </div>
            </div>
          ))}
          <Pagination pagination={pagination} onPageChange={setPage} />
        </div>
      )}
    </div>
  );
}
