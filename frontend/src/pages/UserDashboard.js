import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../contexts/AppContext';
import api from '../lib/api';
import { Calendar, MapPin, Clock, Loader2, Circle, TicketCheck } from 'lucide-react';

const fmt = (iso) => new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
const fmtTime = (iso) => new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

export default function UserDashboard() {
  const { circles, loading: appLoading } = useApp();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/dashboard/').then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (appLoading || loading) return <div className="flex justify-center py-16"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>;

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

  const recentSignups = data?.recent_signups || [];
  const circleEvents = data?.circle_events || [];

  return (
    <div data-testid="user-dashboard">
      {/* Recent signups */}
      <div className="mb-10">
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-black" style={{ fontFamily: 'Outfit' }}>Dashboard</h1>
        <p className="text-xs uppercase tracking-[0.2em] font-bold text-gray-400 mt-4 mb-3">Recent signups</p>
        {recentSignups.length === 0 ? (
          <p className="text-sm text-gray-400 py-4" data-testid="no-recent-signups">No signups yet.</p>
        ) : (
          <div className="border-t border-gray-200">
            {recentSignups.map(s => (
              <Link key={s.id} to={`/events/${s.event.id}`} className="data-row hover:bg-gray-50 transition-colors px-1 block" data-testid={`signup-row-${s.id}`}>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-black truncate">{s.event.title}</p>
                  <div className="flex items-center gap-2 mt-0.5 text-xs text-gray-400">
                    <span>{s.event.circle_name}</span>
                    <span>{fmt(s.event.start_datetime)}</span>
                    {s.event.visibility === 'PUBLIC' && <span className="text-blue-600">Public</span>}
                  </div>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-sm border shrink-0 ${
                  s.status === 'APPROVED' ? 'text-green-700 border-green-200 bg-green-50' :
                  s.status === 'PENDING' ? 'text-amber-700 border-amber-200 bg-amber-50' :
                  'text-red-700 border-red-200 bg-red-50'
                }`}>{s.status}</span>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Events from my circles */}
      <div>
        <p className="text-xs uppercase tracking-[0.2em] font-bold text-gray-400 mb-3">Upcoming from my circles</p>
        {circleEvents.length === 0 ? (
          <p className="text-sm text-gray-400 py-4" data-testid="no-circle-events">No upcoming events.</p>
        ) : (
          <div className="border-t border-gray-200">
            {circleEvents.map(e => (
              <Link key={e.id} to={`/events/${e.id}`} className="data-row hover:bg-gray-50 transition-colors px-1 block" data-testid={`circle-event-${e.id}`}>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-black truncate">{e.title}</p>
                  <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
                    <span>{e.circle_name}</span>
                    <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{fmt(e.start_datetime)}</span>
                    <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{fmtTime(e.start_datetime)}</span>
                    {e.location && <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{e.location}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {e.visibility === 'PUBLIC' && <span className="text-xs px-1.5 py-0.5 rounded-sm border text-blue-600 border-blue-200 bg-blue-50">Public</span>}
                  {e.my_signup_status && (
                    <span className={`text-xs px-2 py-0.5 rounded-sm border ${
                      e.my_signup_status === 'APPROVED' ? 'text-green-700 border-green-200 bg-green-50' :
                      e.my_signup_status === 'PENDING' ? 'text-amber-700 border-amber-200 bg-amber-50' :
                      'text-red-700 border-red-200 bg-red-50'
                    }`}>{e.my_signup_status}</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
