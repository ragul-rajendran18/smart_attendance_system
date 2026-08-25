import styles from './Card.module.css';

export default function Card({
  children,
  className = '',
  accent,
  flat = false,
  interactive = false,
  style,
  ...props
}) {
  return (
    <div
      className={[
        styles.card,
        accent     ? styles.accented     : '',
        flat       ? styles.flat         : '',
        interactive? styles.interactive  : '',
        className,
      ].join(' ')}
      style={{ ...style, ...(accent ? { '--accent-color': accent } : {}) }}
      {...props}
    >
      {children}
    </div>
  );
}
