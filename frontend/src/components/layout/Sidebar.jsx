import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Users, UserPlus, UserCheck, BookOpen,
  Layers, Upload, FileBarChart, User, PlayCircle, Pencil,
  CalendarCheck, PlusCircle, List, CalendarOff,
} from 'lucide-react';
import useAuthStore from '../../store/authStore';
import styles from './Sidebar.module.css';

const NAV = {
  ADMIN: {
    Overview: [
      { to: '/admin', label: 'Dashboard', icon: LayoutDashboard, end: true },
    ],
    Students: [
      { to: '/admin/students',       label: 'Student List',    icon: Users },
      { to: '/admin/create-student', label: 'Add Student',     icon: UserPlus },
    ],
    Staff: [
      { to: '/admin/staff',          label: 'Staff List',      icon: UserCheck },
      { to: '/admin/create-staff',   label: 'Add Staff',       icon: UserPlus },
    ],
    Academics: [
      { to: '/admin/subjects',       label: 'Subject List',    icon: BookOpen },
      { to: '/admin/create-subject', label: 'Add Subject',     icon: PlusCircle },
      { to: '/admin/batches',        label: 'Batches',         icon: Layers },
    ],
    Tools: [
      { to: '/admin/bulk-import',    label: 'Bulk Import',     icon: Upload },
      { to: '/admin/report',         label: 'Weekly Report',   icon: FileBarChart },
      { to: '/admin/holidays',       label: 'Holidays',        icon: CalendarOff },
    ],
  },
  STAFF: {
    Main: [
      { to: '/staff',              label: 'History',         icon: List,          end: true },
      { to: '/staff/session',      label: 'Start Session',   icon: PlayCircle },
      { to: '/staff/edit-session', label: 'Edit Attendance',  icon: Pencil },
      { to: '/staff/profile',      label: 'Profile',         icon: User },
    ],
  },
  STUDENT: {
    Main: [
      { to: '/student',         label: 'Attendance', icon: CalendarCheck, end: true },
      { to: '/student/profile', label: 'Profile',    icon: User },
    ],
  },
};

export default function Sidebar() {
  const { user } = useAuthStore();
  const sections = NAV[user?.role] || {};

  return (
    <aside className={styles.sidebar}>
      {Object.entries(sections).map(([section, items], sIdx) => (
        <div key={section}>
          {sIdx > 0 && <div className={styles.divider} />}
          <div className={styles.section}>
            <span className={styles.sectionLabel}>{section}</span>
          </div>
          <nav className={styles.nav}>
            {items.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  [styles.item, isActive ? styles.active : ''].join(' ')
                }
              >
                <Icon size={15} className={styles.icon} />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      ))}
    </aside>
  );
}
