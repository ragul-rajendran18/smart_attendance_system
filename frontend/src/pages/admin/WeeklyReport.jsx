import { useState, useEffect } from 'react';
import { Download, Info } from 'lucide-react';
import toast from 'react-hot-toast';
import API      from '../../api/client';
import Card     from '../../components/ui/Card';
import Input    from '../../components/ui/Input';
import Select   from '../../components/ui/Select';
import Button   from '../../components/ui/Button';
import PageTitle from '../../components/ui/PageTitle';
import styles   from './Form.module.css';

export default function WeeklyReport() {
  const [form, setForm] = useState({ class_name: '', batch: '', start_date: '', end_date: '' });
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    API.get('/batches/').then(({ data }) => setBatches(data)).catch(() => {});
  }, []);

  const set = (k, v) => setForm((p) => ({ ...p, [k]: v }));

  async function download() {
    if (!form.class_name || !form.batch || !form.start_date || !form.end_date) {
      toast.error('All fields are required'); return;
    }
    if (form.start_date > form.end_date) {
      toast.error('Start date must be before end date'); return;
    }
    setLoading(true);
    const q = new URLSearchParams({
      class_name: form.class_name,
      batch: form.batch,
      start_date: form.start_date,
      end_date: form.end_date,
    });
    try {
      const resp = await fetch(
        `http://127.0.0.1:8000/api/weekly-report/excel/?${q}`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('access')}` } }
      );
      if (!resp.ok) {
        const e = await resp.json().catch(() => ({}));
        toast.error(e.message || 'Failed to generate report'); return;
      }
      const blob = await resp.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href = url;
      a.download = `weekly_report_${form.start_date}_${form.end_date}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success('Report downloaded');
    } catch { toast.error('Network error'); }
    finally { setLoading(false); }
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Download weekly attendance in Excel format">Weekly Report</PageTitle>
      <div className={styles.grid}>
        <Card>
          <div className={styles.formBody}>
            <Input label="Class Name" placeholder="e.g. III IT B"
              value={form.class_name} onChange={(e) => set('class_name', e.target.value)} />
            <Select label="Batch" value={form.batch} onChange={(e) => set('batch', e.target.value)}>
              <option value="">Select a batch</option>
              {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </Select>
            <Input label="Start Date" type="date"
              value={form.start_date} onChange={(e) => set('start_date', e.target.value)} />
            <Input label="End Date"   type="date"
              value={form.end_date}   onChange={(e) => set('end_date',   e.target.value)} />
            <Button onClick={download} loading={loading} variant="success" style={{ width: '100%' }}>
              <Download size={15} /> Download Excel Report
            </Button>
          </div>
        </Card>

        <Card flat>
          <div className={styles.helpHead}><Info size={14} className={styles.helpIcon} />Report limits</div>
          <p className={styles.helpText}>The report checks every period across the selected date range.</p>
          <p className={styles.helpText}>Template supports up to <strong>6 dates</strong> and <strong>71 students</strong>. Requests exceeding these limits return an error.</p>
          <p className={styles.helpText}>Unmarked periods are shown as <strong>N/C</strong>. Sessions that exist but the student has no record show as <strong>M</strong>.</p>
        </Card>
      </div>
    </div>
  );
}
