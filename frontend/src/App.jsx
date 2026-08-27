import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import API from './api/client';
import useAuthStore from './store/authStore';
import ProtectedRoute from './components/ProtectedRoute';
import AppShell from './components/layout/AppShell';

// Public
import Landing from './pages/Landing';

// Auth
import Login from './pages/Login';

// Admin
import AdminDashboard  from './pages/admin/Dashboard';
import CreateStudent   from './pages/admin/CreateStudent';
import StudentList     from './pages/admin/StudentList';
import CreateStaff     from './pages/admin/CreateStaff';
import StaffList       from './pages/admin/StaffList';
import CreateSubject   from './pages/admin/CreateSubject';
import SubjectList     from './pages/admin/SubjectList';
import CreateBatch     from './pages/admin/CreateBatch';
import BulkImport      from './pages/admin/BulkImport';
import WeeklyReport    from './pages/admin/WeeklyReport';
import HolidayList     from './pages/admin/HolidayList';

// Staff
import StaffDashboard  from './pages/staff/Dashboard';
import StaffProfile    from './pages/staff/Profile';
import StartSession    from './pages/staff/StartSession';
import EditSession     from './pages/staff/EditSession';

// Student
import StudentAttendance from './pages/student/Attendance';
import StudentProfile    from './pages/student/Profile';

export default function App() {
  const { access, setUser, logout } = useAuthStore();

  // Rehydrate user from token on mount
  useEffect(() => {
    if (!access) return;
    API.get('/me/')
      .then(({ data }) => setUser(data.data))
      .catch(() => { logout(); });
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />

        {/* ADMIN */}
        <Route path="/admin" element={<ProtectedRoute role="ADMIN"><AppShell /></ProtectedRoute>}>
          <Route index element={<AdminDashboard />} />
          <Route path="students"       element={<StudentList />} />
          <Route path="create-student" element={<CreateStudent />} />
          <Route path="staff"          element={<StaffList />} />
          <Route path="create-staff"   element={<CreateStaff />} />
          <Route path="subjects"       element={<SubjectList />} />
          <Route path="create-subject" element={<CreateSubject />} />
          <Route path="batches"        element={<CreateBatch />} />
          <Route path="bulk-import"    element={<BulkImport />} />
          <Route path="report"         element={<WeeklyReport />} />
          <Route path="holidays"       element={<HolidayList />} />
        </Route>

        {/* STAFF */}
        <Route path="/staff" element={<ProtectedRoute role="STAFF"><AppShell /></ProtectedRoute>}>
          <Route index   element={<StaffDashboard />} />
          <Route path="session" element={<StartSession />} />
          <Route path="edit-session" element={<EditSession />} />
          <Route path="profile" element={<StaffProfile />} />
        </Route>

        {/* STUDENT */}
        <Route path="/student" element={<ProtectedRoute role="STUDENT"><AppShell /></ProtectedRoute>}>
          <Route index   element={<StudentAttendance />} />
          <Route path="profile" element={<StudentProfile />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster position="top-right" toastOptions={{
        style: { background: '#15201E', color: '#F1F5F9', border: '1px solid #2C403E', fontSize: '0.85rem' },
      }} />
    </BrowserRouter>
  );
}
