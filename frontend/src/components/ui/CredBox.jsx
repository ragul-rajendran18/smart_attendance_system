import { CheckCircle, Copy } from 'lucide-react';
import toast from 'react-hot-toast';
import styles from './CredBox.module.css';

function Row({ label, value }) {
  function copy() {
    navigator.clipboard.writeText(value);
    toast.success('Copied to clipboard');
  }
  return (
    <div className={styles.row}>
      <span className={styles.key}>{label}</span>
      <div className={styles.val}>
        <span className={styles.valText}>{value}</span>
        <button className={styles.copy} onClick={copy}>
          <Copy size={11} /> Copy
        </button>
      </div>
    </div>
  );
}

export default function CredBox({ username, password, message }) {
  return (
    <div className={styles.box}>
      {message && (
        <p className={styles.msg}>
          <CheckCircle size={14} />
          {message}
        </p>
      )}
      <Row label="Username" value={username} />
      <Row label="Password" value={password} />
    </div>
  );
}
