import { useState, useEffect } from 'react';
import { Trash2, Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import API       from '../../api/client';
import Card      from '../../components/ui/Card';
import Button    from '../../components/ui/Button';
import Input     from '../../components/ui/Input';
import EmptyState from '../../components/ui/EmptyState';
import PageTitle  from '../../components/ui/PageTitle';
import styles    from './List.module.css';

export default function HolidayList() {
  const [holidays, setHolidays] = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [form,     setForm]     = useState({ date: '', reason: '' });
  const [adding,   setAdding]   = useState(false);

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try {
      const { data } = await API.get('/holidays/');
      setHolidays(data.holidays);
    } catch { toast.error('Failed to load holidays'); }
    finally { setLoading(false); }
  }

  async function addHoliday() {
    if (!form.date || !form.reason) {
      toast.error('Date and reason are required'); return;
    }
    setAdding(true);
    try {
      await API.post('/holidays/create/', {
        date: form.date,
        reason: form.reason,
      });
      toast.success('Holiday added');
      setForm({ date: '', reason: '' });
      load();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to add holiday');
    } finally { setAdding(false); }
  }

  async function remove(id, date) {
    if (!confirm(`Delete holiday on ${date}?`)) return;
    try {
      await API.delete('/holidays/delete/', { data: { id } });
      toast.success('Holiday deleted');
      load();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Delete failed');
    }
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Manage holidays — blocks attendance sessions on selected dates">Holidays</PageTitle>

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className={styles.filterRow}>
          <Input label="Date (DD/MM/YYYY)" placeholder="e.g. 15/08/2026"
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
          />
          <Input label="Reason" placeholder="e.g. Independence Day"
            value={form.reason}
            onChange={(e) => setForm({ ...form, reason: e.target.value })}
            onKeyDown={(e) => e.key === 'Enter' && addHoliday()}
          />
          <Button onClick={addHoliday} loading={adding} variant="primary">
            <Plus size={14} /> Add
          </Button>
        </div>
      </Card>

      {holidays === null && !loading && <EmptyState message="Loading holidays…" />}
      {holidays?.length === 0 && <EmptyState message="No holidays found." sub="Add a holiday above to block attendance on that date." />}
      {holidays?.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>#</th><th>Date</th><th>Reason</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {holidays.map((h, i) => (
                <tr key={h.id}>
                  <td className="text-muted">{i + 1}</td>
                  <td className="mono">{h.date}</td>
                  <td style={{ fontWeight: 500 }}>{h.reason}</td>
                  <td>
                    <div className={styles.actions}>
                      <button className={[styles.iconBtn, styles.del].join(' ')}
                        onClick={() => remove(h.id, h.date)}><Trash2 size={13} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
