import styles from './Input.module.css';

export default function Input({ label, error, className = '', ...props }) {
  return (
    <div className={styles.group}>
      {label && <label className={styles.label}>{label}</label>}
      <input
        className={[
          styles.input,
          error ? styles.hasError : '',
          className,
        ].join(' ')}
        {...props}
      />
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
}
