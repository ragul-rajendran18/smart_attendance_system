import { useState } from 'react';
import { Info } from 'lucide-react';
import toast from 'react-hot-toast';
import API      from '../../api/client';
import Card     from '../../components/ui/Card';
import Input    from '../../components/ui/Input';
import Button   from '../../components/ui/Button';
import CredBox  from '../../components/ui/CredBox';
import PageTitle from '../../components/ui/PageTitle';
import styles   from './Form.module.css';

export default function CreateStaff() {
  const [form, setForm] = useState({ staff_name: '', staff_id: '' });
  const [loading, setLoading] = useState(false);
  const [cred, setCred] = useState(null);

  const set = (k, v) => setForm((p) => ({ ...p, [k]: v }));

  async function submit(e) {
    e.preventDefault();
    if (!form.staff_name || !form.staff_id) { toast.error('All fields are required'); return; }
    setLoading(true);
    try {
      const { data } = await API.post('/create-staff/', form);
      setCred({ username: data.username, password: data.password, message: data.message });
      setForm({ staff_name: '', staff_id: '' });
      toast.success('Staff created successfully');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create staff');
    } finally { setLoading(false); }
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Create a new staff account">Create Staff</PageTitle>
      <div className={styles.grid}>
        <Card>
          <form onSubmit={submit} className={styles.formBody}>
            <Input label="Full Name" placeholder="e.g. Dr. Meena S"
              value={form.staff_name} onChange={(e) => set('staff_name', e.target.value)} />
            <Input label="Staff ID"  placeholder="e.g. STF2024001"
              value={form.staff_id}  onChange={(e) => set('staff_id', e.target.value)} />
            <Button type="submit" variant="primary" loading={loading} style={{ width: '100%' }}>
              Create Staff
            </Button>
          </form>
          {cred && <CredBox {...cred} />}
        </Card>

        <Card flat>
          <div className={styles.helpHead}><Info size={14} className={styles.helpIcon} />How it works</div>
          <p className={styles.helpText}>Enter the staff member's name and unique Staff ID.</p>
          <p className={styles.helpText}>Credentials are auto-generated and can be shared securely from the result box.</p>
        </Card>
      </div>
    </div>
  );
}
