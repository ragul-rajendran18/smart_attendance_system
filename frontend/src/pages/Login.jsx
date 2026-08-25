import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import API from '../api/client';
import useAuthStore from '../store/authStore';
import logo from '../assets/images.jpg';
import styles from './Login.module.css';
import loginBg from '../assets/ChatGPT Image Aug 23, 2026, 08_24_07 PM.png';

export default function Login() {
  const [form, setForm]     = useState({ username: '', password: '' });
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();
  const navigate    = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.username || !form.password) {
      toast.error('Enter your username and password');
      return;
    }
    setLoading(true);
    try {
      const { data } = await API.post('/login/', form);
      setAuth({ role: data.role, username: form.username }, data.access, data.refresh);
      toast.success('Welcome back!');
      const routes = { ADMIN: '/admin', STAFF: '/staff', STUDENT: '/student' };
      navigate(routes[data.role] || '/login');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page} style={{ backgroundImage: `url(${loginBg})` }}>
      <div className={styles.card}>

        {/* ── Card header ── */}
        <div className={styles.head}>
          <img src={logo} alt="Smart Attendance Logo" className={styles.logoImg} />
          <h1 className={styles.title}>Welcome back</h1>
          <p className={styles.sub}>Sign in to Smart Attendance System</p>
        </div>

        {/* ── Form ── */}
        <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.field}>
              <label className={styles.label} htmlFor="username">Username</label>
              <input
                id="username"
                className={styles.input}
                type="text"
                placeholder="Enter your username"
                autoComplete="username"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="password">Password</label>
              <div className={styles.pwWrap}>
                <input
                  id="password"
                  className={styles.input}
                  type={showPw ? 'text' : 'password'}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                />
                <button
                  type="button"
                  className={styles.eyeBtn}
                  onClick={() => setShowPw(!showPw)}
                  aria-label={showPw ? 'Hide password' : 'Show password'}
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" className={styles.submitBtn} disabled={loading}>
              {loading ? <span className="spinner" /> : 'Sign In'}
            </button>
          </form>
      </div>

      <p className={styles.footerText}>
        © {new Date().getFullYear()} Smart Attendance System. All rights reserved.
      </p>
    </div>
  );
}
