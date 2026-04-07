import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Loader2 } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (e) {
      setError(e.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white" data-testid="login-page">
      <div className="w-full max-w-sm px-6">
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-black mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
          Sign in
        </h1>
        <p className="text-sm text-gray-500 mb-8">Welcome back to Circles</p>
        {error && (
          <div className="mb-4 p-3 text-sm text-red-600 border border-red-200 rounded-sm bg-red-50" data-testid="login-error">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email" className="text-xs font-medium uppercase tracking-wider text-gray-500">Email</Label>
            <Input
              id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              className="mt-1.5 rounded-sm border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
              required data-testid="login-email-input" autoComplete="email"
            />
          </div>
          <div>
            <Label htmlFor="password" className="text-xs font-medium uppercase tracking-wider text-gray-500">Password</Label>
            <Input
              id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="mt-1.5 rounded-sm border-gray-300 focus:ring-1 focus:ring-black focus:border-black"
              required data-testid="login-password-input" autoComplete="current-password"
            />
          </div>
          <Button type="submit" className="w-full rounded-sm bg-black text-white hover:bg-gray-800" disabled={loading} data-testid="login-submit-btn">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Sign in'}
          </Button>
        </form>
        <p className="mt-6 text-sm text-gray-500 text-center">
          No account?{' '}
          <Link to="/register" className="text-black font-medium hover:underline" data-testid="register-link">Create one</Link>
        </p>
      </div>
    </div>
  );
}
