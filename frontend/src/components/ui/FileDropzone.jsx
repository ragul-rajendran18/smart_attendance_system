import { useRef, useState } from 'react';
import { UploadCloud, X } from 'lucide-react';
import styles from './FileDropzone.module.css';

export default function FileDropzone({
  onFile,
  accept = '.xlsx,.csv,.pdf',
  label = 'Choose a file to upload',
}) {
  const inputRef = useRef();
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);

  function pick(f) {
    if (!f) return;
    setFile(f);
    onFile(f);
  }

  function clear(e) {
    e.stopPropagation();
    setFile(null);
    onFile(null);
    inputRef.current.value = '';
  }

  return (
    <div
      className={[styles.zone, dragging ? styles.drag : ''].join(' ')}
      onClick={() => inputRef.current.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        pick(e.dataTransfer.files[0]);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className={styles.hidden}
        onChange={(e) => pick(e.target.files[0])}
      />

      {file ? (
        <div className={styles.fileInfo}>
          <span className={styles.fileName}>{file.name}</span>
          <span className={styles.fileSize}>
            {(file.size / 1024).toFixed(1)} KB
          </span>
          <button className={styles.clearBtn} onClick={clear}>
            <X size={14} />
          </button>
        </div>
      ) : (
        <>
          <UploadCloud size={24} className={styles.icon} />
          <span className={styles.mainLabel}>{label}</span>
          <span className={styles.sub}>
            Drag &amp; drop or click to browse &nbsp;·&nbsp; XLSX · CSV · PDF
          </span>
        </>
      )}
    </div>
  );
}
