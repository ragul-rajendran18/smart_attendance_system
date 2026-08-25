import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Play,
  Activity,
  FileSpreadsheet,
  BarChart3,
  Search,
  Check,
  Clock,
  X,
  BadgeCheck,
  ListChecks,
  Upload,
  Layers,
  ScanLine,
  LineChart,
  Download,
  ShieldCheck,
  GraduationCap,
} from 'lucide-react';
import useAuthStore from '../store/authStore';
import logoImg from '../assets/images.jpg';
import landingBg from '../assets/landing-bg.svg';
import styles from './Landing.module.css';

const DASHBOARD = { ADMIN: '/admin', STAFF: '/staff', STUDENT: '/student' };

const STUDENTS = [
  { name: 'Arun Kumar',   status: 'Present', cls: styles.stPresent },
  { name: 'Priya S',      status: 'Present', cls: styles.stPresent },
  { name: 'Karthik R',    status: 'Present', cls: styles.stPresent },
  { name: 'Rahul M',      status: 'Late',    cls: styles.stLate },
  { name: 'Naveen K',     status: 'Absent',  cls: styles.stAbsent },
];

const STATUS_ICON = {
  Present: <Check size={11} strokeWidth={3} />,
  Late:    <Clock size={11} strokeWidth={2.5} />,
  Absent:  <X size={11} strokeWidth={3} />,
};

const CHECKLIST = ['Take Attendance', 'Manage Sessions', 'Export Reports'];

const ROLES = [
  {
    icon: ShieldCheck,
    name: 'Admin',
    desc: 'Manage students, staff, classes, and reports.',
    cls: '',
  },
  {
    icon: ScanLine,
    name: 'Staff',
    desc: 'Take attendance and manage live sessions.',
    cls: styles.roleActive,
  },
  {
    icon: GraduationCap,
    name: 'Student',
    desc: 'View attendance percentage and records.',
    cls: '',
  },
];

const FLOW = [
  { icon: Upload,        num: '01', label: 'Upload'   },
  { icon: Layers,        num: '02', label: 'Organize' },
  { icon: ScanLine,      num: '03', label: 'Track'    },
  { icon: LineChart,     num: '04', label: 'Analyze'  },
  { icon: Download,      num: '05', label: 'Export'   },
];
const FLOW_TOPS = [96, 42, 118, 34, 88];

export default function Landing() {
  const { access, user } = useAuthStore();
  const dashboardPath = DASHBOARD[user?.role] || '/';

  return (
    <div className={styles.page} style={{ backgroundImage: `url(${landingBg})` }}>

      {/* ── Floating pill navbar ── */}
      <header className={styles.navWrap}>
        <nav className={styles.pill}>
          <Link to="/" className={styles.brand}>
            <img src={logoImg} alt="AttendSync Logo" className={styles.brandMarkImg} />
            AttendSync
          </Link>
          <div className={styles.navLinks}>
            <a href="#platform" className={styles.navLink}>Platform</a>
            <span className={styles.navDot}>·</span>
            <a href="#how-it-works" className={styles.navLink}>How It Works</a>
            <span className={styles.navDot}>·</span>
            <a href="#roles" className={styles.navLink}>Roles</a>
            <span className={styles.navDot}>·</span>
            <a href="#resources" className={styles.navLink}>Resources</a>
          </div>
          <div className={styles.navActions}>
            {access ? (
              <Link to={dashboardPath} className={styles.btnDark}>
                Dashboard <ArrowRight size={14} />
              </Link>
            ) : (
              <>
                <Link to="/login" className={styles.navLink}>Sign In</Link>
                <Link to="/login" className={styles.btnDark}>
                  Get Started <ArrowRight size={14} />
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>

      {/* ── Hero ── */}
      <section className={styles.hero}>
        <div className={styles.heroLeft}>
          <h1 className={styles.h1}>
            Focus on <span className={styles.accent}>Learning,</span><br />
            We&rsquo;ll Handle the<br />
            <span className={styles.accent}>Attendance.</span>
          </h1>
          <p className={styles.heroSub}>
            A modern, role-based platform to manage students, classes, staff,
            and attendance — all in one place.
          </p>
          <div className={styles.ctaRow}>
            <Link to="/login" className={styles.btnDarkLg}>
              Start Free <ArrowRight size={16} />
            </Link>
            <a href="#platform" className={styles.btnGhostLg}>
              <span className={styles.playChip}><Play size={11} /></span>
              Watch Demo
            </a>
          </div>
          <div className={styles.indicators}>
            <span className={styles.indicator}><Activity size={13} /> Live Tracking</span>
            <span className={styles.indSep}>·</span>
            <span className={styles.indicator}><FileSpreadsheet size={13} /> Excel Import</span>
            <span className={styles.indSep}>·</span>
            <span className={styles.indicator}><BarChart3 size={13} /> Instant Reports</span>
          </div>
        </div>

        {/* ── Floating dashboard composition ── */}
        <div id="platform" className={styles.dashStage}>

          {/* main card */}
          <div className={`${styles.card} ${styles.dashMain}`}>
            <div className={styles.dashHead}>
              <span className={styles.avatar}>RS</span>
              <div>
                <p className={styles.dashGreet}>Good Morning, Faculty 👋</p>
                <p className={styles.dashDate}>Tuesday · Period 3 in progress</p>
              </div>
            </div>

            <div className={styles.searchBox}>
              <Search size={14} />
              Search student…
            </div>

            <div className={styles.listHead}>
              <span>Today&rsquo;s Attendance</span>
              <span className={styles.listCount}>24 students</span>
            </div>

            <ul className={styles.studentList}>
              {STUDENTS.map((s) => (
                <li key={s.name} className={styles.studentRow}>
                  <span className={styles.studentName}>{s.name}</span>
                  <span className={`${styles.statusPill} ${s.cls}`}>
                    {STATUS_ICON[s.status]} {s.status}
                  </span>
                </li>
              ))}
            </ul>

            <div className={styles.markedBar}>
              <div className={styles.markedTrack}><span style={{ width: '92%' }} /></div>
              <p className={styles.markedLabel}>Marked 22 / 24 · updated live</p>
            </div>
          </div>

          {/* widget — attendance ring */}
          <div className={`${styles.card} ${styles.widget} ${styles.wPct}`}>
            <svg viewBox="0 0 60 60" className={styles.ringSvg}>
              <circle cx="30" cy="30" r="24" fill="none" stroke="#E3EDEB" strokeWidth="6" />
              <circle
                cx="30" cy="30" r="24" fill="none" stroke="#4F6F6C" strokeWidth="6"
                strokeLinecap="round" strokeDasharray="138.8 150.8"
                transform="rotate(-90 30 30)"
              />
            </svg>
            <div className={styles.wPctText}>
              <p className={styles.wBig}>92%</p>
              <p className={styles.wLabel}>Overall<br />Attendance</p>
            </div>
          </div>

          {/* widget — weekly chart */}
          <div className={`${styles.card} ${styles.widget} ${styles.wChart}`}>
            <p className={styles.wTitle}>This week</p>
            <svg viewBox="0 0 100 40" className={styles.chartSvg}>
              <rect x="4"  y="24" width="10" height="12" rx="2.5" fill="#DCE7E5" />
              <rect x="22" y="16" width="10" height="20" rx="2.5" fill="#7F9593" opacity="0.55" />
              <rect x="40" y="20" width="10" height="16" rx="2.5" fill="#DCE7E5" />
              <rect x="58" y="10" width="10" height="26" rx="2.5" fill="#AAB9B7" opacity="0.7" />
              <rect x="76" y="4"  width="10" height="32" rx="2.5" fill="#4F6F6C" />
            </svg>
          </div>

          {/* widget — notification */}
          <div className={`${styles.card} ${styles.widget} ${styles.wNotif}`}>
            <BadgeCheck size={16} className={styles.notifIcon} />
            <div>
              <p className={styles.notifTitle}>New Session Started</p>
              <p className={styles.notifSub}>Physics · Period 3</p>
            </div>
          </div>

          {/* widget — classes today */}
          <div className={`${styles.card} ${styles.widget} ${styles.wClasses}`}>
            <p className={styles.wBig}>24</p>
            <p className={styles.wLabel}>Classes Today</p>
          </div>

          {/* widget — floating checklist */}
          <div className={`${styles.card} ${styles.widget} ${styles.wChecklist}`}>
            <p className={styles.wTitle}><ListChecks size={13} /> My Day</p>
            <ul className={styles.checkList}>
              {CHECKLIST.map((item, i) => (
                <li key={item} className={i === 0 ? styles.done : ''}>
                  <span className={styles.checkSquare}>{i === 0 && <Check size={9} strokeWidth={3.5} />}</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* ── Scattered statistics field ── */}
      <section className={styles.statsField}>
        <svg viewBox="0 0 1000 300" preserveAspectRatio="none" className={styles.statsLines}>
          <path d="M340 70 C420 130 480 190 600 210 S800 120 900 110"
                fill="none" stroke="#7F9593" strokeWidth="1.4" strokeDasharray="2 7" opacity="0.5" />
          <circle cx="340" cy="70" r="3.5" fill="#4F6F6C" />
          <circle cx="620" cy="205" r="3.5" fill="#4F6F6C" />
          <circle cx="900" cy="110" r="3.5" fill="#4F6F6C" />
        </svg>

        <div className={`${styles.statFloat} ${styles.s1}`}>
          <p className={styles.statNum}>10,000+</p>
          <p className={styles.statCap}>Attendance Records</p>
        </div>
        <div className={`${styles.statFloat} ${styles.s2}`}>
          <p className={styles.statNum}>50+</p>
          <p className={styles.statCap}>Classes Managed</p>
        </div>
        <div className={`${styles.statFloat} ${styles.s3}`}>
          <p className={styles.statNumSm}><span className="pulse-dot" /> Real-time</p>
          <p className={styles.statCap}>Tracking</p>
        </div>
        <div className={`${styles.statFloat} ${styles.s4}`}>
          <p className={styles.statNum}>3</p>
          <p className={styles.statCap}>User Roles</p>
        </div>
      </section>

      {/* ── Role panels ── */}
      <section id="roles" className={styles.rolesSection}>
        <h2 className={styles.sectionTitle}>One platform, three experiences</h2>
        <div className={styles.rolesWrap}>
          {ROLES.map(({ icon: Icon, name, desc, cls }) => (
            <div key={name} className={`${styles.rolePanel} ${cls}`}>
              <span className={`${styles.roleIconBox} ${cls ? styles.roleIconBoxActive : ''}`}>
                <Icon size={19} />
              </span>
              <h3 className={styles.roleName}>{name}</h3>
              <p className={styles.roleDesc}>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Workflow journey ── */}
      <section id="how-it-works" className={styles.flowSection}>
        <h2 className={styles.sectionTitle}>From upload to insight, in five steps</h2>
        <div className={styles.flowField}>
          <svg viewBox="0 0 1000 260" preserveAspectRatio="none" className={styles.flowCurve}>
            <path d="M60 128 C140 62 200 58 280 72 S430 168 500 146 S650 36 720 64 S880 142 940 116"
                  fill="none" stroke="#7F9593" strokeWidth="1.6" strokeDasharray="2 8" opacity="0.55" />
          </svg>
          {FLOW.map(({ icon: Icon, num, label }, i) => (
            <div key={num} className={styles.flowNode} style={{ left: `${6 + i * 22}%`, top: FLOW_TOPS[i] }}>
              <div className={styles.flowCircle}>
                <Icon size={21} strokeWidth={1.8} />
                <span className={styles.flowNum}>{num}</span>
              </div>
              <p className={styles.flowLabel}>{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Wave CTA ── */}
      <section id="resources" className={styles.ctaWaveSection}>
        <div className={styles.ctaWaveArt} aria-hidden="true">
          <svg viewBox="0 0 1200 400" preserveAspectRatio="none">
            <path d="M0 210 C160 120 300 250 520 200 C740 152 900 60 1200 150 L1200 400 L0 400 Z"
                  fill="#EAF1EF" />
            <path d="M0 268 C220 190 380 300 620 252 C840 208 980 130 1200 220 L1200 400 L0 400 Z"
                  fill="#DCE7E5" />
            <path d="M0 320 C240 250 420 350 680 306 C900 270 1020 210 1200 275"
                  fill="none" stroke="#7F9593" strokeWidth="1.5" strokeDasharray="2 8" opacity="0.5" />
          </svg>
        </div>
        <div className={styles.ctaContent}>
          <h2 className={styles.ctaTitle}>Ready to transform your attendance process?</h2>
          <p className={styles.ctaSub}>
            Join institutions moving toward smarter attendance management.
          </p>
          <div className={styles.ctaRow}>
            <Link to="/login" className={styles.btnDarkLg}>
              Get Started Free <ArrowRight size={16} />
            </Link>
            <a href="#resources" className={styles.btnOutlineTeal}>Contact Us</a>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className={styles.footer}>
        <span className={styles.footerBrand}>
          <img src={logoImg} alt="AttendSync Logo" className={styles.brandMarkSmallImg} />
          AttendSync
        </span>
        <span>© {new Date().getFullYear()} AttendSync · Smart Academic Attendance Management</span>
      </footer>
    </div>
  );
}
