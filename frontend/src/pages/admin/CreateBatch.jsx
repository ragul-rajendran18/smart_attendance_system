import { useState, useEffect } from 'react';
import { Info } from 'lucide-react';
import toast from 'react-hot-toast';
import API      from '../../api/client';
import Card     from '../../components/ui/Card';
import Input    from '../../components/ui/Input';
import Button   from '../../components/ui/Button';
import PageTitle from '../../components/ui/PageTitle';
import styles   from './Form.module.css';

export default function CreateBatch() {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [batches, setBatches] = useState([]);

  useEffect(() => { load(); }, []);

  async function load() {
    try { const { data } = await API.get('/batches/'); setBatches(data); } catch {}
  }

  async function submit(e) {
    e.preventDefault();
    if (!name.trim()) { toast.error('Batch name is required'); return; }
    setLoading(true);
    try {
      await API.post('/create-batch/', { name });
      toast.success('Batch created');
      setName('');
      load();
    } catch (err) {
      toast.error(err.response?.data?.name?.[0] || err.response?.data?.message || 'Failed');
    } finally { setLoading(false); }
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Add a new admission batch">Create Batch</PageTitle>
      <div className={styles.grid}>
        <Card>
          <form onSubmit={submit} className={styles.formBody}>
            <Input label="Batch Name" placeholder="e.g. 2023-2027" maxLength={20}
              value={name} onChange={(e) => setName(e.target.value)} />
            <Button type="submit" variant="primary" loading={loading} style={{ width: '100%' }}>
              Create Batch
            </Button>
          </form>
          {batches.length > 0 && (
            <div>
              <p style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px', margin: '1.25rem 0 0.6rem' }}>
                Active Batches
              </p>
              <div className={styles.tagList}>
                {batches.map((b) => (
                  <span key={b.id} className={styles.tag}>{b.name}</span>
                ))}
              </div>
            </div>
          )}
        </Card>

        <Card flat>
          <div className={styles.helpHead}><Info size={14} className={styles.helpIcon} />Batch format</div>
          <p className={styles.helpText}>Use admission year and graduation year — e.g. <strong>2023-2027</strong>.</p>
          <p className={styles.helpText}>Batches are used to group students. New batches can be added here at any time without changing the application code.</p>
        </Card>
      </div>
    </div>
  );
}
