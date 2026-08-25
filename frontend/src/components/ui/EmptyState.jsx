import { Inbox } from 'lucide-react';
import styles from './EmptyState.module.css';

export default function EmptyState({ message = 'No data found.', sub, icon: Icon = Inbox }) {
  return (
    <div className={styles.wrap}>
      <Icon size={32} className={styles.icon} strokeWidth={1.5} />
      <p className={styles.msg}>{message}</p>
      {sub && <p className={styles.sub}>{sub}</p>}
    </div>
  );
}
