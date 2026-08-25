import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import API      from '../../api/client';
import Card     from '../../components/ui/Card';
import Select   from '../../components/ui/Select';
import Button   from '../../components/ui/Button';
import PageTitle from '../../components/ui/PageTitle';
import styles   from './StartSession.module.css';

const SCHEDULE = [
  [1,'09:00','09:50'],[2,'09:50','10:40'],[3,'10:55','11:45'],[4,'11:45','12:35'],
  [5,'13:20','14:10'],[6,'14:10','15:00'],[7,'15:10','15:55'],[8,'15:55','16:40'],
];

export default function StartSession() {
  const [classes,  setClasses]  = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [form,     setForm]     = useState({ class_name: '', subject_id: '' });
  const [session,  setSession]  = useState(null);
  const [students, setStudents] = useState([]);
  const [starting, setStarting] = useState(false);
  const [saving,   setSaving]   = useState(false);

  useEffect(() => {
    API.get('/staff/classes/')
      .then(({ data }) => setClasses(data.classes || []))
      .catch(() => {});
  }, []);

  async function onClassChange(cls) {
    setForm({ class_name: cls, subject_id: '' });
    setSubjects([]);
    if (!cls) return;
    try {
      const { data } = await API.get(`/staff/class-subjects/?class_name=${encodeURIComponent(cls)}`);
      setSubjects(data.subjects || []);
    } catch {}
  }

  async function start() {
    if (!form.class_name || !form.subject_id) {
      toast.error('Select a class and subject'); return;
    }
    setStarting(true);
    try {
      const { data } = await API.post('/staff/start-session/', {
        class_name: form.class_name,
        subject_id: parseInt(form.subject_id),
      });
      setSession({ id: data.session_id, period: data.period, class_name: data.class_name, subject: data.subject });
      setStudents(data.students.map((s) => ({ ...s, status: 'Present' })));
      toast.success(data.message);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to start session');
    } finally { setStarting(false); }
  }

  function toggle(id, status) {
    setStudents((prev) => prev.map((s) => s.id === id ? { ...s, status } : s));
  }

  function markAll(status) {
    setStudents((prev) => prev.map((s) => ({ ...s, status })));
  }

  async function save() {
    if (!session) return;
    setSaving(true);
    try {
      await API.post('/staff/save-attendance/', {
        session_id: session.id,
        attendance: students.map((s) => ({ student_id: s.id, status: s.status })),
      });
      toast.success('Attendance saved successfully');
      setSession(null); setStudents([]);
      setForm({ class_name: '', subject_id: '' });
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to save');
    } finally { setSaving(false); }
  }

  const present = students.filter((s) => s.status === 'Present').length;
  const absent  = students.length - present;

  return (
    <div className="fade-up">
      <PageTitle sub="Mark attendance for the current period">Start Session</PageTitle>

      <div className={styles.grid}>
        <Card>
          <div className={styles.formBody}>
            <Select label="Class" value={form.class_name}
              onChange={(e) => onClassChange(e.target.value)}>
              <option value="">Select a class</option>
              {classes.map((c) => <option key={c} value={c}>{c}</option>)}
            </Select>
            <Select label="Subject" value={form.subject_id}
              disabled={!subjects.length}
              onChange={(e) => setForm({ ...form, subject_id: e.target.value })}>
              <option value="">
                {subjects.length ? 'Select a subject' : 'Select a class first'}
              </option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>{s.subject_code} · {s.subject_name}</option>
              ))}
            </Select>
            <Button onClick={start} loading={starting} variant="primary" style={{ width: '100%' }}>
              Start Session
            </Button>
          </div>
        </Card>

        <Card flat>
          <p className={styles.schedTitle}>Period Schedule</p>
          <div className={styles.schedList}>
            {SCHEDULE.map(([p, s, e]) => (
              <div key={p} className={styles.schedRow}>
                <span className={styles.pNum}>P{p}</span>
                <span className={styles.pTime}>{s} – {e}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {session && (
        <>
          <div className={styles.banner}>
            <div className={styles.bannerLeft}>
              <span className="pulse-dot" />
              {session.subject} &nbsp;·&nbsp; {session.class_name}
              <span className={styles.bannerMeta}>
                Period {session.period} · Session #{session.id}
              </span>
            </div>
            <div className={styles.counters}>
              <span className="text-success">{present} Present</span>
              <span className={styles.countSep}>/</span>
              <span className="text-danger">{absent} Absent</span>
            </div>
          </div>

          <div className={styles.toolbar}>
            <Button onClick={() => markAll('Present')} variant="outline" size="sm">
              Mark All Present
            </Button>
            <Button onClick={() => markAll('Absent')} variant="outline" size="sm">
              Mark All Absent
            </Button>
            <Button onClick={save} loading={saving} variant="success" className={styles.save}>
              Save Attendance
            </Button>
          </div>

          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr><th>#</th><th>Register No.</th><th>Student Name</th><th>Status</th></tr>
              </thead>
              <tbody>
                {students.map((s, i) => (
                  <tr key={s.id}>
                    <td className="text-muted">{i + 1}</td>
                    <td className="mono">{s.register_no}</td>
                    <td style={{ fontWeight: 500 }}>{s.student_name}</td>
                    <td>
                      <div className={styles.toggle}>
                        <button
                          className={[styles.tBtn, s.status === 'Present' ? styles.present : ''].join(' ')}
                          onClick={() => toggle(s.id, 'Present')}
                        >Present</button>
                        <button
                          className={[styles.tBtn, s.status === 'Absent' ? styles.absent : ''].join(' ')}
                          onClick={() => toggle(s.id, 'Absent')}
                        >Absent</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
