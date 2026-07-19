import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.status === 401
          ? 'Identifiants invalides'
          : 'Impossible de contacter le serveur'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <form onSubmit={handleSubmit} style={styles.card}>
        <h1 style={styles.title}>🌙 MoonPilot</h1>
        <p style={styles.subtitle}>Administration</p>

        <label style={styles.label}>Nom d'utilisateur</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={styles.input}
          autoFocus
          required
        />

        <label style={styles.label}>Mot de passe</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
          required
        />

        {error && <div style={styles.error}>{error}</div>}

        <button type="submit" style={styles.button} disabled={loading}>
          {loading ? 'Connexion…' : 'Se connecter'}
        </button>
      </form>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#0f172a',
    fontFamily: 'system-ui, sans-serif',
  },
  card: {
    background: '#fff',
    padding: '40px',
    borderRadius: '12px',
    width: '360px',
    boxShadow: '0 10px 40px rgba(0,0,0,.3)',
    display: 'flex',
    flexDirection: 'column',
  },
  title: { margin: 0, fontSize: '28px', textAlign: 'center' },
  subtitle: {
    margin: '4px 0 28px',
    textAlign: 'center',
    color: '#64748b',
    fontSize: '14px',
  },
  label: { fontSize: '13px', color: '#334155', marginBottom: '6px' },
  input: {
    padding: '10px 12px',
    marginBottom: '18px',
    border: '1px solid #cbd5e1',
    borderRadius: '6px',
    fontSize: '14px',
    outline: 'none',
  },
  button: {
    padding: '12px',
    background: '#2f73f2',
    color: '#fff',
    border: 'none',
    borderRadius: '6px',
    fontSize: '15px',
    cursor: 'pointer',
    marginTop: '8px',
  },
  error: {
    background: '#fee2e2',
    color: '#b91c1c',
    padding: '10px',
    borderRadius: '6px',
    fontSize: '13px',
    marginBottom: '12px',
  },
};