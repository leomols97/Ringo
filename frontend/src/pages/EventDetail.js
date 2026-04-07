import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import { Calendar, MapPin, Clock, ArrowLeft, Loader2, Globe, Lock } from 'lucide-react';
import { toast } from '../components/ui/sonner';

export default function EventDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [signing, setSigning] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get(`/events/${id}/`).then(r => setEvent(r.data)).catch(e => setError(e.response?.data?.error || 'Event not found')).finally(() => setLoading(false));
  }, [id]);

  const handleSignup = async () => {
    setSigning(true); setError('');
    try {
      await api.post(`/events/${id}/signup/`);
      const r = await api.get(`/events/${id}/`);
      setEvent(r.data);
      toast.success('Signup request sent');
    } catch (e) {
      const msg = e.response?.data?.error || 'Signup failed';
      setError(msg);
      toast.error(msg);
    } finally {
      setSigning(false);
    }
  };

  const fmt = (iso) => new Date(iso).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  const fmtTime = (iso) => new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  if (loading) return <div className="flex justify-center py-16"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>;
  if (!event) return <div className="empty-state"><p className="text-sm text-gray-500">{error || 'Event not found'}</p></div>;

  return (
    <div data-testid="event-detail-page">
      <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-xs text-gray-400 hover:text-black transition-colors mb-6" data-testid="back-btn">
        <ArrowLeft className="h-3.5 w-3.5" /> Back
      </button>

      <div className="flex items-center gap-2">
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-black" style={{ fontFamily: 'Outfit' }} data-testid="event-title">
          {event.title}
        </h1>
        {event.visibility === 'PUBLIC' ? (
          <span className="text-xs px-1.5 py-0.5 rounded-sm border text-blue-600 border-blue-200 bg-blue-50 flex items-center gap-1"><Globe className="h-3 w-3" />Public</span>
        ) : (
          <span className="text-xs px-1.5 py-0.5 rounded-sm border text-gray-500 border-gray-200 flex items-center gap-1"><Lock className="h-3 w-3" />Private</span>
        )}
      </div>

      {event.circle_name && <p className="text-xs text-gray-400 mt-1">{event.circle_name}</p>}

      <div className="flex flex-wrap items-center gap-4 mt-4 text-sm text-gray-500">
        <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4" />{fmt(event.start_datetime)}</span>
        <span className="flex items-center gap-1.5"><Clock className="h-4 w-4" />{fmtTime(event.start_datetime)} - {fmtTime(event.end_datetime)}</span>
        {event.location && <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4" />{event.location}</span>}
      </div>

      {event.description && (
        <div className="mt-6 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap" data-testid="event-description">{event.description}</div>
      )}

      {error && <div className="mt-4 p-3 text-sm text-red-600 border border-red-200 rounded-sm bg-red-50" data-testid="event-error">{error}</div>}

      <div className="mt-8 pt-6 border-t border-gray-200">
        {event.my_signup_status ? (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Your signup status:</span>
            <span className={`text-sm font-medium px-2.5 py-1 rounded-sm border ${
              event.my_signup_status === 'APPROVED' ? 'text-green-700 border-green-200 bg-green-50' :
              event.my_signup_status === 'PENDING' ? 'text-amber-700 border-amber-200 bg-amber-50' :
              'text-red-700 border-red-200 bg-red-50'
            }`} data-testid="event-signup-status">{event.my_signup_status}</span>
          </div>
        ) : (
          <Button onClick={handleSignup} className="rounded-sm bg-black text-white hover:bg-gray-800" disabled={signing} data-testid="event-signup-btn">
            {signing ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Request to join'}
          </Button>
        )}
      </div>
    </div>
  );
}
