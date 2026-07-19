import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Generations from './pages/Generations';
import Layout from './components/Layout';
import { tokenStore } from './api';
import Prompts from './pages/Prompts';

function Protected({ children }: { children: React.ReactNode }) {
  if (!tokenStore.access) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
        <Route path="/users" element={<Protected><Users /></Protected>} />
        <Route path="/generations" element={<Protected><Generations /></Protected>} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
        <Route path="/prompts" element={<Protected><Prompts /></Protected>} />
      </Routes>
    </BrowserRouter>
  );
}
