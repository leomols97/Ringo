import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import UserDashboard from './pages/UserDashboard';
import Profile from './pages/Profile';
import MyCircles from './pages/MyCircles';
import EventDetail from './pages/EventDetail';
import AdminDashboard from './pages/AdminDashboard';
import AdminMembers from './pages/AdminMembers';
import AdminInvites from './pages/AdminInvites';
import AdminEvents from './pages/AdminEvents';
import AdminEventSignups from './pages/AdminEventSignups';
import SiteManagerDashboard from './pages/SiteManagerDashboard';
import SiteManagerCircles from './pages/SiteManagerCircles';
import InviteAccept from './pages/InviteAccept';
import { Loader2 } from 'lucide-react';
import { Toaster } from './components/ui/sonner';
import './App.css';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
    </div>
  );
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function P({ children }) {
  return <ProtectedRoute><Layout>{children}</Layout></ProtectedRoute>;
}

function AppRoutes() {
  const { user, loading } = useAuth();
  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
    </div>
  );

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <Register />} />
      <Route path="/invite/:token" element={<InviteAccept />} />
      <Route path="/dashboard" element={<P><UserDashboard /></P>} />
      <Route path="/profile" element={<P><Profile /></P>} />
      <Route path="/circles" element={<P><MyCircles /></P>} />
      <Route path="/events/:id" element={<P><EventDetail /></P>} />
      <Route path="/admin" element={<P><AdminDashboard /></P>} />
      <Route path="/admin/members" element={<P><AdminMembers /></P>} />
      <Route path="/admin/invites" element={<P><AdminInvites /></P>} />
      <Route path="/admin/events" element={<P><AdminEvents /></P>} />
      <Route path="/admin/events/:id/signups" element={<P><AdminEventSignups /></P>} />
      <Route path="/site" element={<P><SiteManagerDashboard /></P>} />
      <Route path="/site/circles" element={<P><SiteManagerCircles /></P>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppProvider>
          <AppRoutes />
          <Toaster />
        </AppProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
