import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Loader2 } from 'lucide-react';

export default function Register() {
  const [form, setForm] = useState({ firstName: '', lastName: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const update = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form.firstName, form.lastName, form.email, form.password);
      navigate('/dashboard');
    } catch (e) {
      setError(e.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white" data-testid="register-page">
      <div className="w-full max-w-sm px-6">
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-black mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Create account
        </h1>
        <p className="text-sm text-gray-500 mb-8">Join the Circles community</p>
        {error && (
          <div className="mb-4 p-3 text-sm text-red-600 border border-red-200 rounded-sm bg-red-50" data-testid="register-error">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="fn" className="text-xs font-medium uppercase tracking-wider text-gray-500">First name</Label>
              <Input id="fn" value={form.firstName} onChange={(e) => update('firstName', e.target.value)}
                className="mt-1.5 rounded-sm border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                required data-testid="register-first-name-input" />
            </div>
            <div>
              <Label htmlFor="ln" className="text-xs font-medium uppercase tracking-wider text-gray-500">Last name</Label>
              <Input id="ln" value={form.lastName} onChange={(e) => update('lastName', e.target.value)}
                className="mt-1.5 rounded-sm border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
                data-testid="register-last-name-input" />
            </div>
          </div>
          <div>
            <Label htmlFor="email" className="text-xs font-medium uppercase tracking-wider text-gray-500">Email</Label>
            <Input id="email" type="email" value={form.email} onChange={(e) => update('email', e.target.value)}
              className="mt-1.5 rounded-sm border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
              required data-testid="register-email-input" autoComplete="email" />
          </div>
          <div>
            <Label htmlFor="password" className="text-xs font-medium uppercase tracking-wider text-gray-500">Password</Label>
            <Input id="password" type="password" value={form.password} onChange={(e) => update('password', e.target.value)}
              className="mt-1.5 rounded-sm border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
              required minLength={6} data-testid="register-password-input" autoComplete="new-password" />
          </div>
          <Button type="submit" className="w-full rounded-sm bg-black text-white hover:bg-gray-800" disabled={loading} data-testid="register-submit-btn">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create account'}
          </Button>
        </form>
        <p className="mt-6 text-sm text-gray-500 text-center">
          Already have an account?{' '}
          <Link to="/login" className="text-black font-medium hover:underline" data-testid="login-link">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
