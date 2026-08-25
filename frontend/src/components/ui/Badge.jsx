import styles from './Badge.module.css';

const variantMap = {
  ADMIN:     'warning',
  STAFF:     'primary',
  STUDENT:   'success',
  ACTIVE:    'success',
  COMPLETED: 'neutral',
  Present:   'success',
  Absent:    'danger',
};

export default function Badge({ label, variant, dot = false }) {
  const v = variant || variantMap[label] || 'primary';
  return (
    <span className={[styles.badge, styles[v]].join(' ')}>
      {dot && <span className={styles.dot} />}
      {label}
    </span>
  );
}
