import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import { useNavigate, Link } from 'react-router-dom';
import api from '../lib/api';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { Loader2, Circle } from 'lucide-react';
import { toast } from '../components/ui/sonner';

export default function Profile() {
  const { user, refreshUser, logout } = useAuth();
  const { circles } = useApp();
  const navigate = useNavigate();
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '' });
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) setForm({ first_name: user.first_name || '', last_name: user.last_name || '', email: user.email || '', phone: user.phone || '' });
  }, [user]);

  const update = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const handleSave = async (e) => {
    e.preventDefault(); setSaving(true); setError('');
    try { await api.patch('/profile/', form); await refreshUser(); toast.success('Profile updated'); }
    catch (e) { setError(e.response?.data?.error || 'Failed to save'); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.post('/profile/delete/');
      toast.success('Account removed');
      await logout();
      navigate('/');
    } catch (e) {
      const msg = e.response?.data?.error || 'Failed to delete account';
      setError(msg); toast.error(msg); setDeleting(false);
    }
  };

  return (
    <div data-testid="profile-page">
      <h1 className="section-title">Profile</h1>
      <p className="section-subtitle">Manage your account information</p>

      <form onSubmit={handleSave} className="mt-8 max-w-md space-y-4">
        {error && <div className="p-3 text-sm text-red-600 border border-red-200 rounded-sm bg-red-50" data-testid="profile-error">{error}</div>}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">First name</Label>
            <Input value={form.first_name} onChange={e => update('first_name', e.target.value)} className="mt-1.5 rounded-sm" required data-testid="profile-first-name" />
          </div>
          <div>
            <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">Last name</Label>
            <Input value={form.last_name} onChange={e => update('last_name', e.target.value)} className="mt-1.5 rounded-sm" data-testid="profile-last-name" />
          </div>
        </div>
        <div>
          <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">Email</Label>
          <Input type="email" value={form.email} onChange={e => update('email', e.target.value)} className="mt-1.5 rounded-sm" required data-testid="profile-email" />
        </div>
        <div>
          <Label className="text-xs font-medium uppercase tracking-wider text-gray-500">Phone</Label>
          <Input type="tel" value={form.phone} onChange={e => update('phone', e.target.value)} className="mt-1.5 rounded-sm" placeholder="+1 234 567 8900" data-testid="profile-phone" />
        </div>
        <Button type="submit" className="rounded-sm bg-black text-white hover:bg-gray-800" disabled={saving} data-testid="profile-save-btn">
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save changes'}
        </Button>
      </form>

      <div className="mt-10 pt-8 border-t border-gray-200 max-w-md">
        <h2 className="text-lg font-medium tracking-tight text-black" style={{ fontFamily: 'Outfit' }}>My circles</h2>
        {circles.length === 0 ? (
          <p className="text-sm text-gray-400 mt-2">You haven't joined any circles yet.</p>
        ) : (
          <div className="mt-3 space-y-1">
            {circles.map(c => (
              <Link key={c.id} to={`/circles/${c.id}`} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 -mx-1 px-1 rounded-sm transition-colors" data-testid={`profile-circle-${c.id}`}>
                <div className="flex items-center gap-2">
                  <Circle className="h-3.5 w-3.5 text-gray-400" />
                  <span className="text-sm text-black">{c.name}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-sm border ${c.role === 'CIRCLE_ADMIN' ? 'text-blue-700 border-blue-200 bg-blue-50' : 'text-gray-500 border-gray-200'}`}>
                  {c.role === 'CIRCLE_ADMIN' ? 'Admin' : 'Member'}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>

      <div className="mt-10 pt-8 border-t border-gray-200 max-w-md">
        <h2 className="text-lg font-medium tracking-tight text-red-600" style={{ fontFamily: 'Outfit' }}>Delete account</h2>
        <p className="text-sm text-gray-500 mt-1">Permanently remove your profile. Your personal data will be erased and cannot be recovered.</p>
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant="outline" className="mt-4 rounded-sm border-red-300 text-red-600 hover:bg-red-50" data-testid="delete-account-trigger-btn">
              Delete my account
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent className="rounded-sm">
            <AlertDialogHeader>
              <AlertDialogTitle>Delete your account?</AlertDialogTitle>
              <AlertDialogDescription>This will permanently erase your personal data (name, email, phone). This action cannot be undone.</AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="rounded-sm">Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete} className="rounded-sm bg-red-600 hover:bg-red-700" disabled={deleting} data-testid="delete-account-confirm-btn">
                {deleting ? 'Deleting...' : 'Delete permanently'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
