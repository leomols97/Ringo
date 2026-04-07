import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api, { initCsrf } from '../lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const res = await api.get('/auth/me/');
      if (res.data.authenticated) {
        setUser(res.data.user);
      } else {
        setUser(false);
      }
    } catch {
      setUser(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login/', { email, password });
    setUser(res.data);
    return res.data;
  };

  const register = async (firstName, lastName, email, password) => {
    const res = await api.post('/auth/register/', {
      first_name: firstName, last_name: lastName, email, password,
    });
    setUser(res.data);
    return res.data;
  };

  const logout = async () => {
    try { await api.post('/auth/logout/'); } catch {}
    setUser(false);
  };

  useEffect(() => {
    initCsrf()
      .catch(() => {})
      .then(() => refreshUser())
      .catch(() => setUser(false))
      .finally(() => setLoading(false));
  }, [refreshUser]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
