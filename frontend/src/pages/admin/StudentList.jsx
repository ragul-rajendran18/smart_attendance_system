import { useState, useEffect } from 'react';
import { Pencil, Trash2, Search } from 'lucide-react';
import toast from 'react-hot-toast';
import API       from '../../api/client';
import Card      from '../../components/ui/Card';
import Button    from '../../components/ui/Button';
import Input     from '../../components/ui/Input';
import Select    from '../../components/ui/Select';
import Modal     from '../../components/ui/Modal';
import EmptyState from '../../components/ui/EmptyState';
import PageTitle  from '../../components/ui/PageTitle';
import styles    from './List.module.css';

export default function StudentList() {
  const [filter, setFilter]   = useState({ class_name: '', batch: '' });
  const [batches, setBatches] = useState([]);
  const [students, setStudents] = useState(null);
  const [loading, setLoading]   = useState(false);
  const [editing, setEditing]   = useState(null);
  const [saving,  setSaving]    = useState(false);

  useEffect(() => {
    API.get('/batches/').then(({ data }) => setBatches(data)).catch(() => {});
  }, []);

  async function search() {
    if (!filter.class_name || !filter.batch) {
      toast.error('Class name and batch are required'); return;
    }
    setLoading(true);
    try {
      const q = new URLSearchParams({ class_name: filter.class_name, batch: filter.batch });
      const { data } = await API.get(`/student-list/?${q}`);
      setStudents(data.students);
    } catch { toast.error('Failed to load students'); }
    finally { setLoading(false); }
  }

  async function save() {
    if (!editing.student_name || !editing.register_no || !editing.class_name || !editing.batch) {
      toast.error('All fields are required'); return;
    }
    setSaving(true);
    try {
      await API.put('/update-student/', editing);
      toast.success('Student updated');
      setEditing(null); search();
    } catch (err) { toast.error(err.response?.data?.message || 'Update failed'); }
    finally { setSaving(false); }
  }

  async function remove(id) {
    if (!confirm('Delete this student and their login account?')) return;
    try {
      await API.delete('/delete-student/', { data: { id } });
      toast.success('Student deleted');
      search();
    } catch { toast.error('Delete failed'); }
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Search and manage student accounts">Student List</PageTitle>

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className={styles.filterRow}>
          <Input label="Class Name" placeholder="e.g. II IT A"
            value={filter.class_name}
            onChange={(e) => setFilter({ ...filter, class_name: e.target.value })}
            onKeyDown={(e) => e.key === 'Enter' && search()}
          />
          <Select label="Batch" value={filter.batch}
            onChange={(e) => setFilter({ ...filter, batch: e.target.value })}>
            <option value="">Select batch</option>
            {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </Select>
          <Button onClick={search} loading={loading} variant="primary">
            <Search size={14} /> Search
          </Button>
        </div>
      </Card>

      {students === null && !loading && (
        <EmptyState message="Enter a class name and batch to search." sub="Results will appear here." />
      )}
      {students?.length === 0 && (
        <EmptyState message="No students found." sub="Try a different class name or batch." />
      )}
      {students?.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>#</th>
                <th>Register No.</th>
                <th>Student Name</th>
                <th>Class</th>
                <th>Batch</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s, i) => (
                <tr key={s.id}>
                  <td className="text-muted">{i + 1}</td>
                  <td className="mono">{s.register_no}</td>
                  <td style={{ fontWeight: 500 }}>{s.student_name}</td>
                  <td>{s.class_name}</td>
                  <td>{s.batch || '—'}</td>
                  <td>
                    <div className={styles.actions}>
                      <button
                        className={[styles.iconBtn, styles.edit].join(' ')}
                        title="Edit" onClick={() => setEditing({ ...s, batch: s.batch_id })}
                      ><Pencil size={13} /></button>
                      <button
                        className={[styles.iconBtn, styles.del].join(' ')}
                        title="Delete" onClick={() => remove(s.id)}
                      ><Trash2 size={13} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={!!editing} onClose={() => setEditing(null)} title="Edit Student">
        {editing && (
          <div className={styles.editForm}>
            <Input label="Student Name" value={editing.student_name}
              onChange={(e) => setEditing({ ...editing, student_name: e.target.value })} />
            <Input label="Register No." value={editing.register_no}
              onChange={(e) => setEditing({ ...editing, register_no: e.target.value })} />
            <Input label="Class Name"   value={editing.class_name}
              onChange={(e) => setEditing({ ...editing, class_name: e.target.value })} />
            <Select label="Batch" value={editing.batch || ''}
              onChange={(e) => setEditing({ ...editing, batch: e.target.value })}>
              <option value="">Select batch</option>
              {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </Select>
            <div className={styles.modalActions}>
              <Button onClick={save} loading={saving} variant="primary">Save Changes</Button>
              <Button onClick={() => setEditing(null)} variant="outline">Cancel</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
