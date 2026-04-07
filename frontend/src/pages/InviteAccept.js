import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import api from '../lib/api';
import { Button } from '../components/ui/button';
import { Loader2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function InviteAccept() {
  const { token } = useParams();
  const { user } = useAuth();
  const { refreshCircles } = useApp();
  const navigate = useNavigate();
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get(`/invites/info/${token}/`).then(r => setInfo(r.data)).catch(() => setError('Invalid invitation')).finally(() => setLoading(false));
  }, [token]);

  const handleAccept = async () => {
    setAccepting(true); setError('');
    try {
      const r = await api.post(`/invites/accept/${token}/`);
      setResult(r.data);
      await refreshCircles();
    } catch (e) {
      setError(e.response?.data?.error || 'Failed to accept invitation');
    } finally {
      setAccepting(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="h-5 w-5 animate-spin text-gray-400" /></div>;

  return (
    <div className="min-h-screen flex items-center justify-center bg-white" data-testid="invite-accept-page">
      <div className="w-full max-w-sm px-6 text-center">
        {result ? (
          <div className="animate-fade-in">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto" />
            <h1 className="text-2xl font-medium tracking-tight text-black mt-4" style={{ fontFamily: 'Outfit' }}>Welcome!</h1>
            <p className="text-sm text-gray-500 mt-2">You've joined <strong>{result.circle?.name}</strong></p>
            <Button asChild className="mt-6 rounded-sm bg-black text-white hover:bg-gray-800" data-testid="go-dashboard-btn">
              <Link to="/dashboard">Go to Dashboard</Link>
            </Button>
          </div>
        ) : error ? (
          <div className="animate-fade-in">
            <XCircle className="h-12 w-12 text-red-500 mx-auto" />
            <h1 className="text-2xl font-medium tracking-tight text-black mt-4" style={{ fontFamily: 'Outfit' }}>Invitation error</h1>
            <p className="text-sm text-red-600 mt-2">{error}</p>
            <Button asChild variant="outline" className="mt-6 rounded-sm" data-testid="invite-home-btn">
              <Link to="/">Go home</Link>
            </Button>
          </div>
        ) : info?.valid ? (
          <div className="animate-fade-in">
            <AlertCircle className="h-12 w-12 text-blue-600 mx-auto" />
            <h1 className="text-2xl font-medium tracking-tight text-black mt-4" style={{ fontFamily: 'Outfit' }}>
              You're invited
            </h1>
            <p className="text-sm text-gray-500 mt-2">
              Join <strong>{info.circle_name}</strong>
            </p>
            {!user ? (
              <div className="mt-6 space-y-2">
                <p className="text-xs text-gray-400">Sign in first to accept this invitation</p>
                <Button asChild className="w-full rounded-sm bg-black text-white hover:bg-gray-800" data-testid="invite-login-btn">
                  <Link to={`/login?next=/invite/${token}`}>Sign in</Link>
                </Button>
                <Button asChild variant="outline" className="w-full rounded-sm" data-testid="invite-register-btn">
                  <Link to={`/register?next=/invite/${token}`}>Create account</Link>
                </Button>
              </div>
            ) : (
              <Button onClick={handleAccept} className="mt-6 rounded-sm bg-black text-white hover:bg-gray-800" disabled={accepting} data-testid="invite-accept-btn">
                {accepting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Accept invitation'}
              </Button>
            )}
          </div>
        ) : (
          <div className="animate-fade-in">
            <XCircle className="h-12 w-12 text-gray-400 mx-auto" />
            <h1 className="text-2xl font-medium tracking-tight text-black mt-4" style={{ fontFamily: 'Outfit' }}>Invalid invitation</h1>
            <p className="text-sm text-gray-500 mt-2">This invitation link is expired, already used, or deactivated.</p>
          </div>
        )}
      </div>
    </div>
  );
}
