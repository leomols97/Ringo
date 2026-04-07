import { useApp } from '../contexts/AppContext';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Check, Circle, MapPin } from 'lucide-react';

export default function MyCircles() {
  const { circles, activeCircle, setActiveCircle } = useApp();

  if (circles.length === 0) {
    return (
      <div data-testid="my-circles-page">
        <h1 className="section-title">My Circles</h1>
        <div className="empty-state">
          <Circle className="h-10 w-10 text-gray-300" />
          <h2 className="text-lg font-medium text-black mt-4" style={{ fontFamily: 'Outfit' }}>No circles</h2>
          <p className="empty-state-text">You haven't joined any circles yet. Ask for an invitation link.</p>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="my-circles-page">
      <h1 className="section-title">My Circles</h1>
      <p className="section-subtitle mt-1">Click a circle name to view its profile</p>
      <div className="mt-6 border-t border-gray-200">
        {circles.map(c => {
          const isActive = activeCircle?.id === c.id;
          return (
            <div key={c.id} className="data-row px-1" data-testid={`circle-row-${c.id}`}>
              <Link to={`/circles/${c.id}`} className="flex-1 min-w-0 block">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-black">{c.name}</p>
                  {isActive && <span className="text-xs px-1.5 py-0.5 rounded-sm bg-black text-white">Active</span>}
                </div>
                <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-400">
                  <span>{c.role === 'CIRCLE_ADMIN' ? 'Admin' : 'Member'}</span>
                  {c.address && <span className="flex items-center gap-0.5"><MapPin className="h-3 w-3" />{c.address}</span>}
                </div>
              </Link>
              {!isActive && (
                <Button variant="outline" size="sm" className="rounded-sm border-gray-200 text-xs shrink-0"
                  onClick={(e) => { e.preventDefault(); setActiveCircle(c.id); }}
                  data-testid={`set-active-${c.id}`}>
                  <Check className="h-3 w-3 mr-1" /> Set active
                </Button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
