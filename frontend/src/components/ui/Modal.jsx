import { X } from 'lucide-react';
import styles from './Modal.module.css';

export default function Modal({ open, onClose, title, children, width = '480px' }) {
  if (!open) return null;
  return (
    <div className={styles.overlay} onClick={onClose}>
      <div
        className={styles.box}
        style={{ maxWidth: width }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.header}>
          <h3 className={styles.title}>{title}</h3>
          <button className={styles.close} onClick={onClose} aria-label="Close">
            <X size={15} />
          </button>
        </div>
        <div className={styles.body}>{children}</div>
      </div>
    </div>
  );
}
