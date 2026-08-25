import { Outlet } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Topbar from './Topbar';
import Sidebar from './Sidebar';
import styles from './AppShell.module.css';

export default function AppShell() {
  return (
    <div className={styles.shell}>
      <Topbar />
      <div className={styles.body}>
        <Sidebar />
        <main className={styles.main}>
          <Outlet />
        </main>
      </div>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3500,
          style: {
            background: '#fff',
            color: '#0F172A',
            border: '1px solid #E2E8F0',
            borderRadius: '8px',
            fontSize: '0.84rem',
            fontWeight: '500',
            boxShadow: '0 4px 12px rgba(15,23,42,0.10)',
            padding: '10px 14px',
          },
          success: {
            iconTheme: { primary: '#16A34A', secondary: '#F0FDF4' },
          },
          error: {
            iconTheme: { primary: '#DC2626', secondary: '#FEF2F2' },
          },
        }}
      />
    </div>
  );
}
