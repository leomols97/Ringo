import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../contexts/AppContext';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import { Calendar, MapPin, Clock, Loader2, Circle } from 'lucide-react';

export default function UserDashboard() {
  const { activeCircle, circles, loading: appLoading } = useApp();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeCircle) { setEvents([]); setLoading(false); return; }
    setLoading(true);
    api.get('/events/active/').then(r => setEvents(r.data.events || [])).catch(() => setEvents([])).finally(() => setLoading(false));
  }, [activeCircle]);

  if (appLoading) return <div className="flex justify-center py-16"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>;

  if (circles.length === 0) {
    return (
      <div className="empty-state" data-testid="dashboard-empty">
        <Circle className="h-10 w-10 text-gray-300" />
        <h2 className="text-xl font-medium tracking-tight text-black mt-4" style={{ fontFamily: 'Outfit' }}>No circles yet</h2>
        <p className="empty-state-text">Join a circle to see events and connect with your community.</p>
        <p className="text-xs text-gray-400 mt-2">Ask a circle admin for an invitation link.</p>
      </div>
    );
  }

  if (!activeCircle) {
    return (
      <div className="empty-state" data-testid="dashboard-no-active">
        <Circle className="h-10 w-10 text-gray-300" />
        <h2 className="text-xl font-medium tracking-tight text-black mt-4" style={{ fontFamily: 'Outfit' }}>Select a circle</h2>
        <p className="empty-state-text">Use the circle selector in the navigation to choose your active circle.</p>
      </div>
    );
  }

  const fmt = (iso) => {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };
  const fmtTime = (iso) => {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div data-testid="user-dashboard">
      <div className="mb-8">
        <p className="text-xs uppercase tracking-[0.2em] font-bold text-gray-400">{activeCircle.name}</p>
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-black mt-1" style={{ fontFamily: 'Outfit' }}>
          Upcoming Events
        </h1>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>
      ) : events.length === 0 ? (
        <div className="empty-state" data-testid="dashboard-no-events">
          <Calendar className="h-8 w-8 text-gray-300" />
          <p className="empty-state-text mt-3">No events in this circle yet.</p>
        </div>
      ) : (
        <div className="space-y-0 border-t border-gray-200">
          {events.map(event => (
            <Link
              key={event.id}
              to={`/events/${event.id}`}
              className="data-row group hover:bg-gray-50 transition-colors px-1 block"
              data-testid={`event-row-${event.id}`}
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-black truncate">{event.title}</p>
                <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                  <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{fmt(event.start_datetime)}</span>
                  <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{fmtTime(event.start_datetime)}</span>
                  {event.location && <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{event.location}</span>}
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {event.my_signup_status && (
                  <span className={`text-xs px-2 py-0.5 rounded-sm border ${
                    event.my_signup_status === 'APPROVED' ? 'text-green-700 border-green-200 bg-green-50' :
                    event.my_signup_status === 'PENDING' ? 'text-amber-700 border-amber-200 bg-amber-50' :
                    'text-red-700 border-red-200 bg-red-50'
                  }`} data-testid={`signup-status-${event.id}`}>
                    {event.my_signup_status}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
