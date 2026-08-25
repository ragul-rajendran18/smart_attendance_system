import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import API from '../../api/client';
import useAuthStore from '../../store/authStore';
import Badge from '../ui/Badge';
import logo from '../../assets/images.jpg';
import styles from './Topbar.module.css';

export default function Topbar() {
  const { user, refresh, logout } = useAuthStore();
  const navigate = useNavigate();

  async function handleLogout() {
    try { await API.post('/logout/', { refresh }); } catch {}
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
  }

  return (
    <header className={styles.bar}>
      <div className={styles.brand}>
        <img src={logo} alt="Smart Attendance Logo" className={styles.logoImg} />
        <span className={styles.name}>Smart Attendance</span>
      </div>
      <div className={styles.right}>
        {user && <Badge label={user.role} />}
        <span className={styles.username}>{user?.name || user?.username}</span>
        <button className={styles.logoutBtn} onClick={handleLogout}>
          <LogOut size={14} />
          Logout
        </button>
      </div>
    </header>
  );
}
