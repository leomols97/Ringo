import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { ArrowRight } from 'lucide-react';

export default function Home() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white" data-testid="home-page">
      <p className="text-xs uppercase tracking-[0.25em] font-bold text-gray-400 mb-4" style={{ fontFamily: 'IBM Plex Sans, sans-serif' }}>
        Community Platform
      </p>
      <h1 className="text-4xl sm:text-5xl lg:text-6xl font-medium tracking-tighter text-black" data-testid="home-heading" style={{ fontFamily: 'Outfit, sans-serif' }}>
        Hello World
      </h1>
      <p className="mt-4 text-base text-gray-500 max-w-md text-center leading-relaxed" style={{ fontFamily: 'IBM Plex Sans, sans-serif' }}>
        A multi-circle community where people connect, organize events, and build together.
      </p>
      <div className="mt-10 flex gap-3">
        {user ? (
          <Button asChild className="rounded-sm bg-black text-white hover:bg-gray-800 gap-2" data-testid="go-to-dashboard-btn">
            <Link to="/dashboard">Go to Dashboard <ArrowRight className="h-4 w-4" /></Link>
          </Button>
        ) : (
          <>
            <Button asChild className="rounded-sm bg-black text-white hover:bg-gray-800" data-testid="home-login-btn">
              <Link to="/login">Sign in</Link>
            </Button>
            <Button asChild variant="outline" className="rounded-sm border-gray-200 hover:bg-gray-50" data-testid="home-register-btn">
              <Link to="/register">Create account</Link>
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
