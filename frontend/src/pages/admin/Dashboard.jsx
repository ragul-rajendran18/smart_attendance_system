import { useEffect, useState } from 'react';
import {
  Users, UserCheck, BookOpen, Layers,
  CalendarCheck, CheckCircle2, Info,
  CalendarOff,
} from 'lucide-react';
import API from '../../api/client';
import StatCard  from '../../components/ui/StatCard';
import PageTitle from '../../components/ui/PageTitle';
import styles    from './Dashboard.module.css';

const CARDS = [
  { label: 'Total Students',   key: 'total_students',    icon: Users,         accent: '#304443', iconBg: '#EBF1F0' },
  { label: 'Total Staff',      key: 'total_staff',       icon: UserCheck,     accent: '#46615F', iconBg: '#EEF3F2' },
  { label: 'Subjects',         key: 'total_subjects',    icon: BookOpen,      accent: '#5A7B77', iconBg: '#F0F5F4' },
  { label: 'Active Batches',   key: 'total_batches',     icon: Layers,        accent: '#D97706', iconBg: '#FFFBEB' },
  { label: "Today's Sessions", key: 'todays_sessions',   icon: CalendarCheck, accent: '#16A34A', iconBg: '#F0FDF4' },
  { label: 'Completed Today',  key: 'todays_completed',  icon: CheckCircle2,  accent: '#16A34A', iconBg: '#F0FDF4' },
  { label: 'Upcoming Holidays', key: 'upcoming_holidays', icon: CalendarOff,  accent: '#DC2626', iconBg: '#FEF2F2' },
];

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    API.get('/admin/dashboard/')
      .then(({ data }) => setStats(data.data))
      .catch(() => {});
  }, []);

  return (
    <div className="fade-up">
      <PageTitle sub="Overview of your institution's attendance data">
        Dashboard
      </PageTitle>

      <div className={styles.grid}>
        {CARDS.map(({ label, key, icon, accent, iconBg }) => (
          <StatCard
            key={key}
            label={label}
            value={stats?.[key]}
            icon={icon}
            accent={accent}
            iconBg={iconBg}
          />
        ))}
      </div>

      <div className={styles.hint}>
        <Info size={15} className={styles.hintIcon} />
        <p className={styles.hintText}>
          Use the sidebar to manage students, staff, subjects and batches.
          Run bulk imports from Excel, CSV or PDF files.
          Download weekly attendance reports in the standard Excel template format.
        </p>
      </div>
    </div>
  );
}
