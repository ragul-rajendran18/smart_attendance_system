import styles from './PageTitle.module.css';

export default function PageTitle({ children, sub, action }) {
  return (
    <div className={styles.wrap}>
      <div>
        <h1 className={styles.title}>{children}</h1>
        {sub && <p className={styles.sub}>{sub}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
