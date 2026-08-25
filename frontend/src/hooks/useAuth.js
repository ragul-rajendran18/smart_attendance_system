import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/client';
import useAuthStore from '../store/authStore';

export function useBootstrap() {
  const { access, setUser, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!access) return;
    API.get('/me/')
      .then(({ data }) => setUser(data.data))
      .catch(() => { logout(); navigate('/login'); });
  }, []);
}
