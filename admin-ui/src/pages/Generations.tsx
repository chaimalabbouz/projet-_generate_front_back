import { useEffect, useState } from 'react';
import { getGenerations } from '../api';

export default function Generations() {
  const [gens, setGens] = useState<any[]>([]);
  const [open, setOpen] = useState<number | null>(null);

  useEffect(() => {
    getGenerations().then(setGens).catch(console.error);
  }, []);

  const badge = (status: string) => {
    const ok = ['success', 'succeeded'].includes((status || '').toLowerCase());
    return {
      ...s.badge,
      background: ok ? '#dcfce7' : '#fee2e2',
      color: ok ? '#166534' : '#b91c1c',
    };
  };

  const parse = (m: any) => {
    if (!m) return null;
    try {
      return typeof m === 'string' ? JSON.parse(m) : m;
    } catch {
      return null;
    }
  };

  return (
    <div>
      <h1 style={s.h1}>Générations ({gens.length})</h1>
      <div style={s.panel}>
        <table style={s.table}>
          <thead>
            <tr>
              <th style={s.th}>#</th>
              <th style={s.th}>Utilisateur</th>
              <th style={s.th}>Figma ID</th>
              <th style={s.th}>Statut</th>
              <th style={s.th}>Date</th>
              <th style={s.th}></th>
            </tr>
          </thead>
          <tbody>
            {gens.map((g) => {
              const m = parse(g.metrics);
              return (
                <>
                  <tr key={g.id}>
                    <td style={s.td}>{g.id}</td>
                    <td style={s.td}>{g.github_login ? `@${g.github_login}` : '—'}</td>
                    <td style={{ ...s.td, fontFamily: 'monospace', fontSize: 12 }}>
                      {g.figma_file_id?.slice(0, 22)}
                    </td>
                    <td style={s.td}>
                      <span style={badge(g.status)}>{g.status}</span>
                    </td>
                    <td style={s.td}>
                      {g.started_at ? new Date(g.started_at).toLocaleString('fr-FR') : '—'}
                    </td>
                    <td style={s.td}>
                      {m && (
                        <button
                          onClick={() => setOpen(open === g.id ? null : g.id)}
                          style={s.btn}
                        >
                          {open === g.id ? 'Masquer' : 'Métriques'}
                        </button>
                      )}
                    </td>
                  </tr>
                  {open === g.id && m && (
                    <tr key={`${g.id}-detail`}>
                      <td colSpan={6} style={s.detail}>
                        <div style={s.metricGrid}>
                          {m.planner && <Metric label="Planner" value={`${m.planner.duration_s}s`} />}
                          {m.backend && (
                            <>
                              <Metric label="Backend" value={`${m.backend.duration_s}s`} />
                              <Metric
                                label="Entités"
                                value={`${m.backend.entities_passed}/${m.backend.entities_total}`}
                              />
                              <Metric label="Réussite" value={`${m.backend.success_rate_pct}%`} />
                            </>
                          )}
                          {m.design && <Metric label="Design" value={`${m.design.duration_s}s`} />}
                          {m.frontend && (
                            <Metric label="Pages bindées" value={m.frontend.pages_bound} />
                          )}
                          {m.pipeline && (
                            <>
                              <Metric label="Total" value={`${m.pipeline.total_real_s}s`} />
                              <Metric
                                label="Gain parallélisme"
                                value={`${m.pipeline.parallelism_gain_pct}%`}
                              />
                            </>
                          )}
                        </div>
                        {g.error_message && (
                          <div style={s.error}>{g.error_message}</div>
                        )}
                      </td>
                    </tr>
                  )}
                </>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: any }) {
  return (
    <div style={s.metric}>
      <div style={s.metricValue}>{value}</div>
      <div style={s.metricLabel}>{label}</div>
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
  badge: { padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 500 },
  btn: {
    padding: '4px 10px',
    fontSize: 12,
    border: '1px solid #cbd5e1',
    background: '#fff',
    borderRadius: 5,
    cursor: 'pointer',
  },
  detail: { padding: 20, background: '#f8fafc', borderTop: '1px solid #e2e8f0' },
  metricGrid: { display: 'flex', gap: 28, flexWrap: 'wrap' },
  metric: {},
  metricValue: { fontSize: 18, fontWeight: 600, color: '#0f172a' },
  metricLabel: { fontSize: 12, color: '#64748b' },
  error: {
    marginTop: 14,
    padding: 10,
    background: '#fee2e2',
    color: '#b91c1c',
    borderRadius: 6,
    fontSize: 12,
    fontFamily: 'monospace',
  },
};