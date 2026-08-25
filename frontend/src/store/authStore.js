import { create } from 'zustand';

const useAuthStore = create((set) => ({
  user: null,       // { id, username, role, name, ... }
  access: localStorage.getItem('access') || null,
  refresh: localStorage.getItem('refresh') || null,

  setAuth: (user, access, refresh) => {
    localStorage.setItem('access', access);
    localStorage.setItem('refresh', refresh);
    set({ user, access, refresh });
  },

  setUser: (user) => set({ user }),

  logout: () => {
    localStorage.clear();
    set({ user: null, access: null, refresh: null });
  },
}));

export default useAuthStore;
