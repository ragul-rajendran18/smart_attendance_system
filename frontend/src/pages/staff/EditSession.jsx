import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import API from '../../api/client';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import PageTitle from '../../components/ui/PageTitle';
import styles from './EditSession.module.css';

const SCHEDULE = [
  [1,'09:00','09:50'],[2,'09:50','10:40'],[3,'10:55','11:45'],[4,'11:45','12:35'],
  [5,'13:20','14:10'],[6,'14:10','15:00'],[7,'15:10','15:55'],[8,'15:55','16:40'],
];

function getActivePeriodNow() {
  const now = new Date();
  const ct = now.getHours() * 60 + now.getMinutes();
  for (const [p, s, e] of SCHEDULE) {
    const [sh, sm] = s.split(':').map(Number);
    const [eh, em] = e.split(':').map(Number);
    if (ct >= sh * 60 + sm && ct < eh * 60 + em) return { period: p, start: s, end: e };
  }
  return null;
}

function getTodayKey() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export default function EditSession() {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);
  const [students, setStudents] = useState([]);
  const [saving, setSaving] = useState(false);
  const [activePeriod, setActivePeriod] = useState(null);
  const [allSessions, setAllSessions] = useState([]);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    const ap = getActivePeriodNow();
    setActivePeriod(ap);
    fetchSessions(ap);
  }, []);

  async function fetchSessions(ap) {
    setLoading(true);
    try {
      const { data } = await API.get('/staff/session-list/');
      const today = getTodayKey();
      const sessions = (data.sessions || []).filter(s => s.date === today && s.status === 'COMPLETED');
      setAllSessions(sessions);
      if (ap && sessions.length > 0) {
        const match = sessions.find(s => s.period === ap.period);
        if (match) {
          await loadSession(match.id);
          return;
        }
      }
    } catch {}
    setLoading(false);
  }

  async function loadSession(id) {
    try {
      const { data } = await API.get(`/staff/session-attendance/?session_id=${id}`);
      if (data.session.status === 'COMPLETED') {
        setSession(data.session);
        setStudents(data.students.map(s => ({ ...s, originalStatus: s.status })));
        setEditMode(true);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to load session');
    }
    setLoading(false);
  }

  function toggle(id, status) {
    setStudents(prev => prev.map(s => s.id === id ? { ...s, status } : s));
  }

  function markAll(status) {
    setStudents(prev => prev.map(s => ({ ...s, status })));
  }

  const changedCount = students.filter(s => s.status !== s.originalStatus).length;
  const present = students.filter(s => s.status === 'Present').length;
  const absent = students.length - present;

  async function save() {
    if (!session) return;
    setSaving(true);
    try {
      await API.put('/staff/edit-attendance/', {
        session_id: session.id,
        attendance: students.map(s => ({ student_id: s.id, status: s.status })),
      });
      toast.success('Attendance updated successfully');
      setStudents(prev => prev.map(s => ({ ...s, originalStatus: s.status })));
      setEditMode(false);
      setSession(null);
      setActivePeriod(null);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update attendance');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="fade-up">
        <PageTitle sub="Edit saved attendance">Edit Attendance</PageTitle>
        <div style={{ textAlign: 'center', padding: '3rem' }}><span className="spinner" /></div>
      </div>
    );
  }

  if (editMode && session) {
    return (
      <div className="fade-up">
        <PageTitle sub="Modify attendance within the active session period">Edit Attendance</PageTitle>

        <div className={styles.banner}>
          <div className={styles.bannerLeft}>
            <span className="pulse-dot" />
            {session.subject} &nbsp;&middot;&nbsp; {session.class_name}
            <span className={styles.bannerMeta}>
              Period {session.period} &middot; Session #{session.id}
            </span>
          </div>
          <div className={styles.counters}>
            <span className="text-success">{present} Present</span>
            <span className={styles.countSep}>/</span>
            <span className="text-danger">{absent} Absent</span>
            {changedCount > 0 && (
              <span className={styles.changedBadge}>{changedCount} changed</span>
            )}
          </div>
        </div>

        <div className={styles.toolbar}>
          <Button onClick={() => markAll('Present')} variant="outline" size="sm">Mark All Present</Button>
          <Button onClick={() => markAll('Absent')} variant="outline" size="sm">Mark All Absent</Button>
          <Button onClick={save} loading={saving} variant="success" className={styles.save}>
            Update Attendance
          </Button>
        </div>

        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr><th>#</th><th>Register No.</th><th>Student Name</th><th>Status</th></tr>
            </thead>
            <tbody>
              {students.map((s, i) => (
                <tr key={s.id} className={s.status !== s.originalStatus ? styles.changedRow : ''}>
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
      </div>
    );
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Edit saved attendance within the active session period">Edit Attendance</PageTitle>

      {activePeriod ? (
        <Card>
          <div className={styles.emptyState}>
            <p className={styles.emptyTitle}>No editable session found for Period {activePeriod.period}</p>
            <p className={styles.emptySub}>
              Session time: {activePeriod.start} – {activePeriod.end}
            </p>
            <p className={styles.emptyHint}>
              Attendance can only be edited during the same session period on the same day.
              Save attendance first from Start Session, then return here to edit.
            </p>
          </div>
        </Card>
      ) : (
        <Card>
          <div className={styles.emptyState}>
            <p className={styles.emptyTitle}>No active session period</p>
            <p className={styles.emptySub}>
              Attendance can only be edited during a session period (09:00 – 16:40).
            </p>
            <div className={styles.scheduleGrid}>
              {SCHEDULE.map(([p, s, e]) => (
                <div key={p} className={styles.scheduleItem}>
                  <span className={styles.periodBadge}>P{p}</span>
                  <span className={styles.periodTime}>{s} – {e}</span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {allSessions.length > 0 && (
        <Card style={{ marginTop: '1.25rem' }}>
          <p className={styles.sectionTitle}>Today's Completed Sessions</p>
          <p className={styles.sectionSub}>
            Only sessions from the current active period can be edited.
          </p>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr><th>Period</th><th>Class</th><th>Subject</th><th>Status</th></tr>
              </thead>
              <tbody>
                {allSessions.map(s => (
                  <tr key={s.id}>
                    <td>P{s.period}</td>
                    <td>{s.class_name}</td>
                    <td>{s.subject}</td>
                    <td><Badge label={s.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
