import { useState, useEffect } from 'react';
import { Pencil, Trash2, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import API       from '../../api/client';
import Button    from '../../components/ui/Button';
import Input     from '../../components/ui/Input';
import Modal     from '../../components/ui/Modal';
import EmptyState from '../../components/ui/EmptyState';
import PageTitle  from '../../components/ui/PageTitle';
import styles    from './List.module.css';

export default function StaffList() {
  const [staff,   setStaff]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);
  const [saving,  setSaving]  = useState(false);

  useEffect(() => { load(); }, []);

  async function load() {
    setLoading(true);
    try { const { data } = await API.get('/staff-list/'); setStaff(data.staff || []); }
    catch { toast.error('Failed to load staff'); }
    finally { setLoading(false); }
  }

  async function save() {
    if (!editing.staff_name || !editing.staff_id) {
      toast.error('Name and Staff ID are required'); return;
    }
    setSaving(true);
    try {
      await API.put('/update-staff/', editing);
      toast.success('Staff updated');
      setEditing(null); load();
    } catch (err) { toast.error(err.response?.data?.message || 'Update failed'); }
    finally { setSaving(false); }
  }

  async function remove(id, name) {
    if (!confirm(`Delete ${name} and their login account?`)) return;
    try { await API.delete('/delete-staff/', { data: { id } }); toast.success('Deleted'); load(); }
    catch { toast.error('Delete failed'); }
  }

  return (
    <div className="fade-up">
      <PageTitle
        sub="Manage staff accounts"
        action={
          <Button onClick={load} variant="outline" size="sm">
            <RefreshCw size={13} /> Refresh
          </Button>
        }
      >
        Staff List
      </PageTitle>

      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <span className="spinner" />
        </div>
      )}
      {!loading && staff.length === 0 && <EmptyState message="No staff members found." />}
      {!loading && staff.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>#</th><th>Staff ID</th><th>Staff Name</th>
                <th>Username</th><th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {staff.map((s, i) => (
                <tr key={s.id}>
                  <td className="text-muted">{i + 1}</td>
                  <td className="mono">{s.staff_id}</td>
                  <td style={{ fontWeight: 500 }}>{s.staff_name}</td>
                  <td className="text-muted">{s.username}</td>
                  <td>
                    <div className={styles.actions}>
                      <button className={[styles.iconBtn, styles.edit].join(' ')}
                        onClick={() => setEditing({ ...s, password: '' })}><Pencil size={13} /></button>
                      <button className={[styles.iconBtn, styles.del].join(' ')}
                        onClick={() => remove(s.id, s.staff_name)}><Trash2 size={13} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={!!editing} onClose={() => setEditing(null)} title="Edit Staff Member">
        {editing && (
          <div className={styles.editForm}>
            <Input label="Staff Name" value={editing.staff_name}
              onChange={(e) => setEditing({ ...editing, staff_name: e.target.value })} />
            <Input label="Staff ID"   value={editing.staff_id}
              onChange={(e) => setEditing({ ...editing, staff_id: e.target.value })} />
            <Input label="New Password" type="password"
              placeholder="Leave blank to keep current password"
              value={editing.password}
              onChange={(e) => setEditing({ ...editing, password: e.target.value })} />
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
