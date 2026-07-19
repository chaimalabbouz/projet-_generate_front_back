import { Link, useLocation, useNavigate } from 'react-router-dom';
import { logout } from '../api';

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();

  const links = [
    { to: '/dashboard', label: 'Vue d\'ensemble' },
    { to: '/users', label: 'Utilisateurs' },
    { to: '/generations', label: 'Générations' },
    { to: '/prompts', label: 'Prompts LLM' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={s.shell}>
      <aside style={s.sidebar}>
        <div style={s.brand}>🌙 MoonPilot</div>
        <nav style={s.nav}>
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              style={{
                ...s.link,
                ...(location.pathname === l.to ? s.linkActive : {}),
              }}
            >
              {l.label}
            </Link>
          ))}
        </nav>
        <button onClick={handleLogout} style={s.logout}>
          Se déconnecter
        </button>
      </aside>
      <main style={s.main}>{children}</main>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  shell: { display: 'flex', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' },
  sidebar: {
    width: 230,
    background: '#0f172a',
    color: '#e2e8f0',
    padding: '24px 16px',
    display: 'flex',
    flexDirection: 'column',
  },
  brand: { fontSize: 20, fontWeight: 600, marginBottom: 32, paddingLeft: 8 },
  nav: { display: 'flex', flexDirection: 'column', gap: 4, flex: 1 },
  link: {
    padding: '10px 12px',
    borderRadius: 6,
    color: '#94a3b8',
    textDecoration: 'none',
    fontSize: 14,
  },
  linkActive: { background: '#1e293b', color: '#fff' },
  logout: {
    padding: '10px',
    background: 'transparent',
    border: '1px solid #334155',
    color: '#94a3b8',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 13,
  },
  main: { flex: 1, padding: 32, background: '#f8fafc', overflowY: 'auto' },
};
