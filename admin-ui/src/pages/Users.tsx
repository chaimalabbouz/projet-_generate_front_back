import { useEffect, useState } from 'react';
import { getUsers } from '../api';

export default function Users() {
  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    getUsers().then(setUsers).catch(console.error);
  }, []);

  return (
    <div>
      <h1 style={s.h1}>Utilisateurs ({users.length})</h1>
      <div style={s.panel}>
        <table style={s.table}>
          <thead>
            <tr>
              <th style={s.th}>GitHub</th>
              <th style={s.th}>Nom</th>
              <th style={s.th}>Email</th>
              <th style={s.th}>Générations</th>
              <th style={s.th}>Inscription</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td style={s.td}>@{u.github_login}</td>
                <td style={s.td}>{u.name || '—'}</td>
                <td style={s.td}>{u.email}</td>
                <td style={s.td}>{u.generations_count}</td>
                <td style={s.td}>
                  {u.created_at ? new Date(u.created_at).toLocaleDateString('fr-FR') : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  h1: { margin: '0 0 24px', fontSize: 24 },
  panel: { background: '#fff', borderRadius: 10, border: '1px solid #e2e8f0', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 14 },
  th: {
    textAlign: 'left',
    padding: '12px 16px',
    background: '#f1f5f9',
    color: '#475569',
    fontWeight: 600,
    fontSize: 13,
  },
  td: { padding: '12px 16px', borderTop: '1px solid #f1f5f9' },
};