import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator,
} from '../components/ui/dropdown-menu';
import {
  Select, SelectTrigger, SelectValue, SelectContent, SelectItem,
} from '../components/ui/select';
import { Button } from '../components/ui/button';
import { ChevronDown, User, LogOut, CircleUser, Eye, Shield, Settings } from 'lucide-react';

const viewMeta = {
  user: { label: 'User', icon: Eye },
  admin: { label: 'Admin', icon: Shield },
  site: { label: 'Site Manager', icon: Settings },
};

const navLinks = {
  user: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/circles', label: 'My Circles' },
  ],
  admin: [
    { to: '/admin', label: 'Overview' },
    { to: '/admin/members', label: 'Members' },
    { to: '/admin/invites', label: 'Invites' },
    { to: '/admin/events', label: 'Events' },
  ],
  site: [
    { to: '/site', label: 'Overview' },
    { to: '/site/circles', label: 'Circles' },
  ],
};

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const {
    currentView, setCurrentView, availableViews,
    circles, adminCircles, activeCircle, setActiveCircle,
  } = useApp();
  const navigate = useNavigate();
  const location = useLocation();

  const selectorCircles = currentView === 'admin'
    ? (user?.is_site_manager ? circles : adminCircles)
    : circles;
  const showSelector = selectorCircles.length > 0 && currentView !== 'site';

  const handleViewChange = (view) => {
    setCurrentView(view);
    const defaultRoutes = { user: '/dashboard', admin: '/admin', site: '/site' };
    navigate(defaultRoutes[view]);
  };

  const links = navLinks[currentView] || navLinks.user;
  const ViewIcon = viewMeta[currentView]?.icon || Eye;

  return (
    <div className="min-h-screen bg-white" data-testid="app-layout">
      {/* ── Top bar ── */}
      <nav className="sticky top-0 z-50 bg-white border-b border-gray-200" data-testid="top-navbar">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <Link to="/" className="text-lg font-semibold tracking-tight text-black" data-testid="app-logo" style={{ fontFamily: 'Outfit, sans-serif' }}>
              Circles
            </Link>

            <div className="flex items-center gap-2">
              {/* Role-view dropdown */}
              {availableViews.length > 1 && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm" className="rounded-sm border-gray-200 text-xs gap-1.5" data-testid="role-view-dropdown">
                      <ViewIcon className="h-3.5 w-3.5" />
                      {viewMeta[currentView]?.label}
                      <ChevronDown className="h-3 w-3 opacity-50" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="rounded-sm shadow-none border-gray-200">
                    {availableViews.map(v => {
                      const Icon = viewMeta[v].icon;
                      return (
                        <DropdownMenuItem
                          key={v}
                          onClick={() => handleViewChange(v)}
                          className={`text-xs gap-2 ${currentView === v ? 'bg-gray-100' : ''}`}
                          data-testid={`role-view-${v}`}
                        >
                          <Icon className="h-3.5 w-3.5" />
                          {viewMeta[v].label}
                        </DropdownMenuItem>
                      );
                    })}
                  </DropdownMenuContent>
                </DropdownMenu>
              )}

              {/* Circle selector */}
              {showSelector && (
                <Select
                  value={activeCircle?.id || ''}
                  onValueChange={(val) => setActiveCircle(val)}
                >
                  <SelectTrigger className="w-[160px] sm:w-[200px] rounded-sm border-gray-200 text-xs h-8" data-testid="circle-selector">
                    <SelectValue placeholder="Select circle" />
                  </SelectTrigger>
                  <SelectContent className="rounded-sm shadow-none border-gray-200">
                    {selectorCircles.map(c => (
                      <SelectItem key={c.id} value={c.id} className="text-xs" data-testid={`circle-option-${c.slug || c.id}`}>
                        {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}

              {/* User menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="text-xs gap-1.5" data-testid="user-menu-trigger">
                    <CircleUser className="h-4 w-4" />
                    <span className="hidden sm:inline">{user?.first_name}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="rounded-sm shadow-none border-gray-200 min-w-[140px]">
                  <DropdownMenuItem onClick={() => navigate('/profile')} className="text-xs gap-2" data-testid="profile-menu-item">
                    <User className="h-3.5 w-3.5" /> Profile
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={logout} className="text-xs gap-2 text-red-600 focus:text-red-600" data-testid="logout-menu-item">
                    <LogOut className="h-3.5 w-3.5" /> Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </nav>

      {/* ── Sub-nav ── */}
      <div className="border-b border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-6 h-10 items-end">
            {links.map(link => {
              const active = location.pathname === link.to || (link.to !== '/' && location.pathname.startsWith(link.to + '/'));
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`text-xs font-medium pb-2.5 border-b-2 transition-colors ${
                    active ? 'text-black border-black' : 'text-gray-400 border-transparent hover:text-gray-600'
                  }`}
                  data-testid={`nav-link-${link.label.toLowerCase().replace(' ', '-')}`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Content ── */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
        {children}
      </main>
    </div>
  );
}
