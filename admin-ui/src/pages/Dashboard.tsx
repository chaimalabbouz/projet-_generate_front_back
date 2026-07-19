import { useEffect, useState } from 'react';
import { getStats, getGenerations } from '../api';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [gens, setGens] = useState<any[]>([]);

  useEffect(() => {
    getStats().then(setStats).catch(console.error);
    getGenerations().then(setGens).catch(console.error);
  }, []);

  if (!stats) return <p>Chargement…</p>;

  // durée par service, moyennée sur les générations qui ont des métriques
  const withMetrics = gens.filter((g) => g.metrics);
  const avg = (service: string) => {
    const vals = withMetrics
      .map((g) => {
        const m = typeof g.metrics === 'string' ? JSON.parse(g.metrics) : g.metrics;
        return m?.[service]?.duration_s;
      })
      .filter((v) => typeof v === 'number');
    return vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : 0;
  };

  const chartData = [
    { service: 'Planner', duree: avg('planner') },
    { service: 'Backend', duree: avg('backend') },
    { service: 'Design', duree: avg('design') },
    { service: 'Frontend', duree: avg('frontend') },
  ];

  return (
    <div>
      <h1 style={s.h1}>Vue d'ensemble</h1>

      <div style={s.cards}>
        <Card label="Utilisateurs" value={stats.users} />
        <Card label="Générations" value={stats.generations_total} />
        <Card label="Réussies" value={stats.generations_success} />
        <Card label="Taux de réussite" value={`${stats.success_rate_pct}%`} />
      </div>

      <div style={s.panel}>
        <h2 style={s.h2}>Durée moyenne par service (secondes)</h2>
        {withMetrics.length === 0 ? (
          <p style={s.muted}>Aucune métrique disponible pour l'instant.</p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="service" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="duree" fill="#2f73f2" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

function Card({ label, value }: { label: string; value: any }) {
  return (
    <div style={s.card}>
      <div style={s.cardValue}>{value}</div>
      <div style={s.cardLabel}>{label}</div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  h1: { margin: '0 0 24px', fontSize: 24 },
  h2: { margin: '0 0 16px', fontSize: 16, color: '#334155' },
  cards: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 28 },
  card: {
    background: '#fff',
    padding: '20px',
    borderRadius: 10,
    border: '1px solid #e2e8f0',
  },
  cardValue: { fontSize: 30, fontWeight: 600, color: '#0f172a' },
  cardLabel: { fontSize: 13, color: '#64748b', marginTop: 4 },
  panel: { background: '#fff', padding: 24, borderRadius: 10, border: '1px solid #e2e8f0' },
  muted: { color: '#94a3b8', fontSize: 14 },
};