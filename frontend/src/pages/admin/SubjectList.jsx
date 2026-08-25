import { useState, useEffect } from 'react';
import { Pencil, Trash2, Search } from 'lucide-react';
import toast from 'react-hot-toast';
import API       from '../../api/client';
import Card      from '../../components/ui/Card';
import Button    from '../../components/ui/Button';
import Input     from '../../components/ui/Input';
import Modal     from '../../components/ui/Modal';
import EmptyState from '../../components/ui/EmptyState';
import PageTitle  from '../../components/ui/PageTitle';
import styles    from './List.module.css';

export default function SubjectList() {
  const [className, setClassName] = useState('');
  const [subjects, setSubjects]   = useState(null);
  const [loading,  setLoading]    = useState(false);
  const [editing,  setEditing]    = useState(null);
  const [saving,   setSaving]     = useState(false);

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try {
      const url = className
        ? `/subject-list/?class_name=${encodeURIComponent(className)}`
        : '/subject-list/';
      const { data } = await API.get(url);
      setSubjects(data.subjects);
    } catch { toast.error('Failed to load subjects'); }
    finally { setLoading(false); }
  }

  async function save() {
    if (!editing.subject_code || !editing.subject_name || !editing.class_name) {
      toast.error('All fields are required'); return;
    }
    setSaving(true);
    try {
      await API.put('/update-subject/', editing);
      toast.success('Subject updated');
      setEditing(null); load();
    } catch (err) { toast.error(err.response?.data?.message || 'Update failed'); }
    finally { setSaving(false); }
  }

  async function remove(id, code) {
    if (!confirm(`Delete subject ${code}?`)) return;
    try { await API.delete('/delete-subject/', { data: { id } }); toast.success('Deleted'); load(); }
    catch { toast.error('Delete failed'); }
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Search, edit and delete subjects">Subject List</PageTitle>

      <Card style={{ marginBottom: '1.25rem' }}>
        <div className={styles.filterRow}>
          <Input label="Filter by Class (optional)" placeholder="e.g. II IT A — leave empty for all"
            value={className}
            onChange={(e) => setClassName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && load()}
          />
          <div />
          <Button onClick={load} loading={loading} variant="primary">
            <Search size={14} /> Search
          </Button>
        </div>
      </Card>

      {subjects === null && !loading && <EmptyState message="Loading subjects…" />}
      {subjects?.length === 0 && <EmptyState message="No subjects found." sub="Try a different class name or clear the filter." />}
      {subjects?.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>#</th><th>Code</th><th>Subject Name</th>
                <th>Class</th><th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((s, i) => (
                <tr key={s.id}>
                  <td className="text-muted">{i + 1}</td>
                  <td className="mono">{s.subject_code}</td>
                  <td style={{ fontWeight: 500 }}>{s.subject_name}</td>
                  <td>{s.class_name}</td>
                  <td>
                    <div className={styles.actions}>
                      <button className={[styles.iconBtn, styles.edit].join(' ')}
                        onClick={() => setEditing({ ...s })}><Pencil size={13} /></button>
                      <button className={[styles.iconBtn, styles.del].join(' ')}
                        onClick={() => remove(s.id, s.subject_code)}><Trash2 size={13} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={!!editing} onClose={() => setEditing(null)} title="Edit Subject">
        {editing && (
          <div className={styles.editForm}>
            <Input label="Subject Code" value={editing.subject_code}
              onChange={(e) => setEditing({ ...editing, subject_code: e.target.value })} />
            <Input label="Subject Name" value={editing.subject_name}
              onChange={(e) => setEditing({ ...editing, subject_name: e.target.value })} />
            <Input label="Class Name"   value={editing.class_name}
              onChange={(e) => setEditing({ ...editing, class_name: e.target.value })} />
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
