import { useState } from 'react';
import { Download } from 'lucide-react';
import toast from 'react-hot-toast';
import API          from '../../api/client';
import Card         from '../../components/ui/Card';
import Button       from '../../components/ui/Button';
import FileDropzone from '../../components/ui/FileDropzone';
import PageTitle    from '../../components/ui/PageTitle';
import styles       from './BulkImport.module.css';

function ImportCard({ type, label }) {
  const [file,    setFile]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);

  async function upload() {
    if (!file) { toast.error(`Choose a ${label} file first`); return; }
    const form = new FormData();
    form.append('file', file);
    setLoading(true);
    try {
      const endpoint = type === 'student' ? '/students/bulk-upload/' : '/staff/bulk-upload/';
      const { data } = await API.post(endpoint, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(data);
      toast.success(`${label} import completed`);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Import failed');
    } finally { setLoading(false); }
  }

  async function download() {
    const token = result?.download_token;
    if (!token) { toast.error('No download token available'); return; }
    const ep = type === 'student'
      ? `/students/bulk-upload/download/${token}/`
      : `/staff/bulk-upload/download/${token}/`;
    try {
      const resp = await fetch(`http://127.0.0.1:8000/api${ep}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access')}` },
      });
      if (!resp.ok) { toast.error('Download failed'); return; }
      const blob = await resp.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href = url; a.download = `${type}_import_result.xlsx`;
      a.click(); URL.revokeObjectURL(url);
      toast.success('Result downloaded');
    } catch { toast.error('Network error'); }
  }

  return (
    <Card>
      <div className={styles.cardInner}>
        <div className={styles.cardHead}>
          <div className={[styles.typeIcon, styles[type]].join(' ')}>
            {type === 'student' ? 'ST' : 'SF'}
          </div>
          <div>
            <p className={styles.cardTitle}>{label} Import</p>
            <p className={styles.cardSub}>XLSX · CSV · PDF supported</p>
          </div>
        </div>

        <FileDropzone label={`Choose ${label} file`} onFile={setFile} />

        <div className={styles.uploadActions}>
          <Button onClick={upload} loading={loading} variant="primary" style={{ flex: 1 }}>
            Upload {label}s
          </Button>
          {result?.download_token && (
            <Button onClick={download} variant="outline">
              <Download size={14} />
            </Button>
          )}
        </div>

        {result && (
          <div className={styles.resultBlock}>
            <p className={styles.resultTitle}>{result.source_file}</p>
            <div className={styles.statRow}>
              <div className={styles.stat}>
                <span className={[styles.statN, 'text-success'].join(' ')}>{result.created_count}</span>
                <span className={styles.statL}>Created</span>
              </div>
              <div className={styles.stat}>
                <span className={[styles.statN, 'text-warning'].join(' ')}>{result.ignored_count}</span>
                <span className={styles.statL}>Ignored</span>
              </div>
              <div className={styles.stat}>
                <span className={[styles.statN, 'text-danger'].join(' ')}>{result.failed_count}</span>
                <span className={styles.statL}>Failed</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

export default function BulkImport() {
  return (
    <div className="fade-up">
      <PageTitle sub="Import multiple records from a spreadsheet or PDF">
        Bulk Import
      </PageTitle>

      <div className={styles.grid}>
        <ImportCard type="student" label="Student" />
        <ImportCard type="staff"   label="Staff" />
      </div>

      <Card flat>
        <p className={styles.guideHead}>Supported column names</p>
        <p className={styles.guideText}>
          <strong>Students:</strong> Register No, Student Name, Class Name, Batch.<br />
          <strong>Staff:</strong> Staff Name / Teacher Name / Faculty Name &nbsp;·&nbsp;
          Staff ID / Employee ID.<br />
          Column headers are detected automatically using fuzzy matching —
          minor spelling variations are handled.
        </p>
      </Card>
    </div>
  );
}
