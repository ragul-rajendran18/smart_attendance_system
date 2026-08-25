import { useEffect, useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import API       from '../../api/client';
import Card      from '../../components/ui/Card';
import Badge     from '../../components/ui/Badge';
import StatCard  from '../../components/ui/StatCard';
import PageTitle  from '../../components/ui/PageTitle';
import EmptyState from '../../components/ui/EmptyState';
import styles    from './Attendance.module.css';

export default function StudentAttendance() {
  const [data, setData] = useState(null);

  useEffect(() => {
    API.get('/student/attendance/').then(({ data }) => setData(data)).catch(() => {});
  }, []);

  if (!data) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
      <span className="spinner" />
    </div>
  );

  const pct      = data.attendance_percentage;
  const pctColor = pct >= 75 ? 'var(--success)' : pct >= 60 ? 'var(--warning)' : 'var(--danger)';

  return (
    <div className="fade-up">
      <PageTitle sub="Your attendance record across all subjects">My Attendance</PageTitle>

      <div className={styles.stats}>
        <StatCard label="Total Classes" value={data.total_classes} accent="#304443" iconBg="#EBF1F0" />
        <StatCard label="Present"       value={data.present}       accent="#16A34A" iconBg="#F0FDF4" />
        <StatCard label="Absent"        value={data.absent}        accent="#DC2626" iconBg="#FEF2F2" />
        <StatCard label="Percentage"    value={`${pct}%`}          accent={pctColor} iconBg={pct >= 75 ? '#F0FDF4' : pct >= 60 ? '#FFFBEB' : '#FEF2F2'} />
      </div>

      <Card className={styles.progressCard}>
        <div className={styles.progressHeader}>
          <span className={styles.progressLabel}>Overall Attendance</span>
          <span className={styles.progressPct} style={{ color: pctColor }}>{pct}%</span>
        </div>
        <div className={styles.bar}>
          <div
            className={styles.fill}
            style={{ width: `${Math.min(pct, 100)}%`, background: pctColor }}
          />
        </div>
        {pct < 75 && (
          <p className={styles.warn}>
            <AlertTriangle size={13} />
            Attendance below 75% — you may be barred from examinations.
          </p>
        )}
      </Card>

      {(!data.attendance || data.attendance.length === 0)
        ? <EmptyState message="No attendance records yet." sub="Attend a session to see records here." />
        : (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr><th>Period</th><th>Subject</th><th>Status</th></tr>
              </thead>
              <tbody>
                {data.attendance.map((r, i) => (
                  <tr key={i}>
                    <td className="text-muted">Period {r.period}</td>
                    <td style={{ fontWeight: 500 }}>{r.subject}</td>
                    <td><Badge label={r.status} dot /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      }
    </div>
  );
}
