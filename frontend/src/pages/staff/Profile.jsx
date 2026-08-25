import { useEffect, useState } from 'react';
import API      from '../../api/client';
import Card     from '../../components/ui/Card';
import Badge    from '../../components/ui/Badge';
import PageTitle from '../../components/ui/PageTitle';
import styles   from './Profile.module.css';

export default function StaffProfile() {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    API.get('/staff/profile/').then(({ data }) => setProfile(data)).catch(() => {});
  }, []);

  if (!profile) return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
      <span className="spinner" />
    </div>
  );

  return (
    <div className="fade-up">
      <PageTitle>My Profile</PageTitle>
      <Card style={{ maxWidth: 500 }}>
        <div className={styles.header}>
          <div className={styles.avatar}>
            {profile.staff_name?.[0]?.toUpperCase()}
          </div>
          <div>
            <div className={styles.name}>{profile.staff_name}</div>
            <Badge label={profile.role} />
          </div>
        </div>
        <div className={styles.infoGrid}>
          {[
            { key: 'Username', val: profile.username },
            { key: 'Staff ID', val: profile.staff_id },
            { key: 'Role',     val: profile.role     },
          ].map(({ key, val }) => (
            <div key={key} className={styles.infoItem}>
              <div className={styles.infoKey}>{key}</div>
              <div className={styles.infoVal}>{val}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
