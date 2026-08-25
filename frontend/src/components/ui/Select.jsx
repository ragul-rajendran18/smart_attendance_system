import styles from './Input.module.css';

export default function Select({ label, error, children, className = '', ...props }) {
  return (
    <div className={styles.group}>
      {label && <label className={styles.label}>{label}</label>}
      <select
        className={[
          styles.input,
          error ? styles.hasError : '',
          className,
        ].join(' ')}
        {...props}
      >
        {children}
      </select>
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
}
