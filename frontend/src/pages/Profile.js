import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { Loader2 } from 'lucide-react';

export default function Profile() {
  const { user, refreshUser, logout } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
  });
  const [saving, setSaving] = useState(false);
  const [deactivating, setDeactivating] = useState(false);
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');

  const update = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true); setMsg(''); setError('');
    try {
      await api.patch('/profile/', form);
      await refreshUser();
      setMsg('Profile updated');
    } catch (e) {
      setError(e.response?.data?.error || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async () => {
    setDeactivating(true);
    try {
      await api.post('/profile/deactivate/');
      await logout();
      navigate('/');
    } catch {
      setError('Failed to deactivate account');
      setDeactivating(false);
    }
  };

  return (
    <div data-testid="profile-page">
      <h1 className="section-title">Profile</h1>
      <p className="section-subtitle">Manage your account information</p>

      <form onSubmit={handleSave} className="mt-8 max-w-md space-y-4">
        {msg && <div className="p-3 text-sm text-green-700 border border-green-200 rounded-sm bg-green-50" data-testid="profile-success">{msg}</div>}
        {error && <div className="p-3 text-sm text-red-600 border border-red-200 rounded-sm bg-red-50" data-testid="profile-error">{error}</div>}

        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">First name</Label>
            <Input value={form.first_name} onChange={e => update('first_name', e.target.value)}
              className="mt-1.5 rounded-sm" required data-testid="profile-first-name" />
          </div>
          <div>
            <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">Last name</Label>
            <Input value={form.last_name} onChange={e => update('last_name', e.target.value)}
              className="mt-1.5 rounded-sm" data-testid="profile-last-name" />
          </div>
        </div>
        <div>
          <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">Email</Label>
          <Input type="email" value={form.email} onChange={e => update('email', e.target.value)}
            className="mt-1.5 rounded-sm" required data-testid="profile-email" />
        </div>
        <Button type="submit" className="rounded-sm bg-black text-white hover:bg-gray-800" disabled={saving} data-testid="profile-save-btn">
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save changes'}
        </Button>
      </form>

      <div className="mt-12 pt-8 border-t border-gray-200 max-w-md">
        <h2 className="text-lg font-medium tracking-tight text-red-600" style={{ fontFamily: 'Outfit' }}>Danger zone</h2>
        <p className="text-sm text-gray-500 mt-1">Deactivating your account will log you out and prevent future sign-ins.</p>
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant="outline" className="mt-4 rounded-sm border-red-300 text-red-600 hover:bg-red-50" data-testid="deactivate-trigger-btn">
              Deactivate account
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="rounded-sm">
            <AlertDialogHeader>
              <AlertDialogTitle>Deactivate your account?</AlertDialogTitle>
              <AlertDialogDescription>This action will deactivate your account. You will be signed out immediately.</AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="rounded-sm">Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDeactivate} className="rounded-sm bg-red-600 hover:bg-red-700" disabled={deactivating} data-testid="deactivate-confirm-btn">
                {deactivating ? 'Deactivating...' : 'Deactivate'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
