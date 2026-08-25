import { useState, useEffect } from 'react';
import { Info } from 'lucide-react';
import toast from 'react-hot-toast';
import API      from '../../api/client';
import Card     from '../../components/ui/Card';
import Input    from '../../components/ui/Input';
import Select   from '../../components/ui/Select';
import Button   from '../../components/ui/Button';
import CredBox  from '../../components/ui/CredBox';
import PageTitle from '../../components/ui/PageTitle';
import styles   from './Form.module.css';

export default function CreateStudent() {
  const [form, setForm] = useState({ student_name: '', register_no: '', class_name: '', batch: '' });
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [cred, setCred] = useState(null);

  useEffect(() => {
    API.get('/batches/').then(({ data }) => setBatches(data)).catch(() => {});
  }, []);

  const set = (k, v) => setForm((p) => ({ ...p, [k]: v }));

  async function submit(e) {
    e.preventDefault();
    if (!form.student_name || !form.register_no || !form.class_name || !form.batch) {
      toast.error('All fields are required'); return;
    }
    setLoading(true);
    try {
      const { data } = await API.post('/create-student/', form);
      setCred({ username: data.username, password: data.password, message: data.message });
      setForm({ student_name: '', register_no: '', class_name: '', batch: '' });
      toast.success('Student created successfully');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create student');
    } finally { setLoading(false); }
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Create a new student account">Create Student</PageTitle>
      <div className={styles.grid}>
        <Card>
          <form onSubmit={submit} className={styles.formBody}>
            <Input label="Full Name"     placeholder="e.g. Rajesh Kumar"
              value={form.student_name} onChange={(e) => set('student_name', e.target.value)} />
            <Input label="Register No."  placeholder="e.g. 21CS001"
              value={form.register_no}  onChange={(e) => set('register_no', e.target.value)} />
            <Input label="Class Name"    placeholder="e.g. II IT A"
              value={form.class_name}   onChange={(e) => set('class_name', e.target.value)} />
            <Select label="Batch" value={form.batch} onChange={(e) => set('batch', e.target.value)}>
              <option value="">Select a batch</option>
              {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </Select>
            <Button type="submit" variant="primary" loading={loading} style={{ width: '100%' }}>
              Create Student
            </Button>
          </form>
          {cred && <CredBox {...cred} />}
        </Card>

        <Card flat>
          <div className={styles.helpHead}><Info size={14} className={styles.helpIcon} />How it works</div>
          <p className={styles.helpText}>Fill in the student's details and click <strong>Create Student</strong>.</p>
          <p className={styles.helpText}>The system auto-generates a unique <strong>username</strong> and secure <strong>password</strong> for the student to log in.</p>
          <p className={styles.helpText}>Share the credentials with the student securely. They can be copied directly from the result box.</p>
        </Card>
      </div>
    </div>
  );
}
