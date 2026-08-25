import styles from './StatCard.module.css';

export default function StatCard({
  label,
  value,
  icon: Icon,
  accent = '#304443',
  iconBg = '#EBF1F0',
  sub,
}) {
  return (
    <div
      className={styles.card}
      style={{ '--c': accent, '--icon-bg': iconBg }}
    >
      <div className={styles.top}>
        <span className={styles.label}>{label}</span>
        {Icon && (
          <div className={styles.iconWrap}>
            <Icon size={15} strokeWidth={2} />
          </div>
        )}
      </div>
      <div className={styles.value}>
        {value ?? <span className="spinner" />}
      </div>
      {sub && <div className={styles.sub}>{sub}</div>}
    </div>
  );
}
