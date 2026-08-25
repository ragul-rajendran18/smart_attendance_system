import styles from './Button.module.css';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  className = '',
  ...props
}) {
  return (
    <button
      className={[
        styles.btn,
        styles[variant],
        styles[size],
        props.style?.width === '100%' ? styles.full : '',
        className,
      ].join(' ')}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <span className="spinner" />}
      {children}
    </button>
  );
}
