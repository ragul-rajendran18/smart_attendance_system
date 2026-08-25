import { useEffect, useState } from 'react';
import { Eye } from 'lucide-react';
import API       from '../../api/client';
import Card      from '../../components/ui/Card';
import Badge     from '../../components/ui/Badge';
import PageTitle  from '../../components/ui/PageTitle';
import EmptyState from '../../components/ui/EmptyState';
import styles    from './Dashboard.module.css';

export default function StaffDashboard() {
  const [sessions, setSessions]   = useState(null);
  const [detail,   setDetail]     = useState(null);
  const [loadingD, setLoadingD]   = useState(false);

  useEffect(() => {
    API.get('/staff/session-list/')
      .then(({ data }) => setSessions(data.sessions || []))
      .catch(() => setSessions([]));
  }, []);

  async function viewSession(id) {
    setLoadingD(true);
    try {
      const { data } = await API.get(`/staff/session-attendance/?session_id=${id}`);
      setDetail(data);
    } catch {}
    finally { setLoadingD(false); }
  }

  return (
    <div className="fade-up">
      <PageTitle sub="Your past attendance sessions">Attendance History</PageTitle>

      {sessions === null && (
        <div style={{ textAlign: 'center', padding: '3rem' }}><span className="spinner" /></div>
      )}
      {sessions?.length === 0 && (
        <EmptyState message="No sessions recorded yet." sub="Start a session to see history here." />
      )}
      {sessions?.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Date</th><th>Period</th><th>Class</th>
                <th>Subject</th><th>Status</th><th>P / A</th><th></th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 500 }}>{s.date}</td>
                  <td>P{s.period}</td>
                  <td>{s.class_name}</td>
                  <td>{s.subject}</td>
                  <td><Badge label={s.status} dot /></td>
                  <td>
                    <span className="text-success" style={{ fontWeight: 600 }}>{s.present_count}</span>
                    <span className="text-muted"> / </span>
                    <span className="text-danger"  style={{ fontWeight: 600 }}>{s.absent_count}</span>
                  </td>
                  <td>
                    <button className={styles.viewBtn} onClick={() => viewSession(s.id)}
                      title="View attendance" disabled={loadingD}>
                      <Eye size={13} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {detail && (
        <Card className={styles.detailCard}>
          <p className={styles.detailTitle}>
            Period {detail.session.period} &nbsp;·&nbsp;
            {detail.session.class_name} &nbsp;·&nbsp;
            {detail.session.subject} &nbsp;·&nbsp;
            {detail.session.date}
          </p>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr><th>#</th><th>Reg No.</th><th>Student Name</th><th>Status</th></tr>
              </thead>
              <tbody>
                {detail.students.map((s, i) => (
                  <tr key={s.id}>
                    <td className="text-muted">{i + 1}</td>
                    <td className="mono">{s.register_no}</td>
                    <td style={{ fontWeight: 500 }}>{s.student_name}</td>
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
