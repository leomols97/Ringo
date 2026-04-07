import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import api from '../lib/api';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const { user } = useAuth();
  const [circles, setCircles] = useState([]);
  const [activeCircle, setActiveCircleState] = useState(null);
  const [activeCircleRole, setActiveCircleRole] = useState(null);
  const [currentView, setCurrentView] = useState('user');
  const [loading, setLoading] = useState(true);

  const adminCircles = circles.filter(c => c.role === 'CIRCLE_ADMIN');
  const availableViews = ['user'];
  if (adminCircles.length > 0 || user?.is_site_manager) availableViews.push('admin');
  if (user?.is_site_manager) availableViews.push('site');

  const refreshCircles = useCallback(async () => {
    try {
      const res = await api.get('/circles/mine/');
      setCircles(res.data.circles || []);
    } catch {
      setCircles([]);
    }
  }, []);

  const refreshActiveCircle = useCallback(async () => {
    try {
      const res = await api.get('/circles/active/');
      setActiveCircleState(res.data.circle);
      setActiveCircleRole(res.data.role);
    } catch {
      setActiveCircleState(null);
      setActiveCircleRole(null);
    }
  }, []);

  const setActiveCircle = useCallback(async (circleId) => {
    try {
      const res = await api.post('/circles/active/', { circle_id: circleId || null });
      setActiveCircleState(res.data.circle);
      setActiveCircleRole(res.data.role);
    } catch (e) {
      console.error('Failed to set active circle', e);
    }
  }, []);

  useEffect(() => {
    if (user && user !== false) {
      setLoading(true);
      Promise.all([refreshCircles(), refreshActiveCircle()]).finally(() => setLoading(false));
    } else {
      setCircles([]);
      setActiveCircleState(null);
      setActiveCircleRole(null);
      setCurrentView('user');
      setLoading(false);
    }
  }, [user, refreshCircles, refreshActiveCircle]);

  useEffect(() => {
    if (!availableViews.includes(currentView)) {
      setCurrentView('user');
    }
  }, [availableViews, currentView]);

  return (
    <AppContext.Provider value={{
      circles, adminCircles, activeCircle, activeCircleRole,
      currentView, setCurrentView, availableViews,
      setActiveCircle, refreshCircles, refreshActiveCircle, loading,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be inside AppProvider');
  return ctx;
}
