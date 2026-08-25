import { Navigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

export default function ProtectedRoute({ children, role }) {
  const { access, user } = useAuthStore();
  if (!access) return <Navigate to="/login" replace />;
  if (role && user && user.role !== role) {
    const map = { ADMIN: '/admin', STAFF: '/staff', STUDENT: '/student' };
    return <Navigate to={map[user.role] || '/login'} replace />;
  }
  return children;
}
