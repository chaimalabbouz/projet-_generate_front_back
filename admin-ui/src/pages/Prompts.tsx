import { useEffect, useState } from 'react';
import {
  getPrompts, getPrompt, updatePrompt, getModels, updateConfig,
} from '../api';

export default function Prompts() {
  const [prompts, setPrompts] = useState<any[]>([]);
  const [models, setModels] = useState<any[]>([]);
  const [editing, setEditing] = useState<any | null>(null);
  const [text, setText] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const load = () => getPrompts().then(setPrompts).catch(console.error);

  useEffect(() => {
    load();
    getModels().then(setModels).catch(console.error);
  }, []);

  const openEditor = async (row: any) => {
    const full = await getPrompt(row.prompt_id);
    setEditing({ ...row, ...full });
    setText(full.prompt);
    setMessage('');
  };

  const savePrompt = async () => {
    setSaving(true);
    setMessage('');
    try {
      await updatePrompt(editing.prompt_id, text);
      setMessage('✅ Prompt enregistré');
      await load();
    } catch {
      setMessage('❌ Échec de l\'enregistrement');
    } finally {
      setSaving(false);
    }
  };

  const saveConfig = async (row: any, field: string, value: any) => {
    try {
      await updateConfig(row.config_id, { [field]: value });
      await load();
    } catch {
      alert('Échec de la mise à jour');
    }
  };

  return (
    <div>
      <h1 style={s.h1}>Prompts &amp; configuration LLM</h1>
      <p style={s.hint}>
        Ces prompts sont utilisés par le service Design (pipeline Figma).
        Toute modification est prise en compte au prochain run, sans redéploiement.
      </p>

      <div style={s.panel}>
        <table style={s.table}>
          <thead>
            <tr>
              <th style={s.th}>Nom</th>
              <th style={s.th}>Modèle</th>
              <th style={s.th}>Température</th>
              <th style={s.th}>Max tokens</th>
              <th style={s.th}>Version</th>
              <th style={s.th}>Taille</th>
              <th style={s.th}></th>
            </tr>
          </thead>
          <tbody>
            {prompts.map((p) => (
              <tr key={p.prompt_id}>
                <td style={s.td}>
                  <strong>{p.nom_prompt}</strong>
                  <div style={s.preview}>{p.preview}…</div>
                </td>
                <td style={s.td}>
                  <select
                    value={p.model_id ?? ''}
                    onChange={(e) => saveConfig(p, 'model_id', Number(e.target.value))}
                    style={s.select}
                  >
                    {models.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.model_name}
                      </option>
                    ))}
                  </select>
                </td>
                <td style={s.td}>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="2"
                    defaultValue={p.temperature ?? 0}
                    onBlur={(e) => saveConfig(p, 'temperature', Number(e.target.value))}
                    style={s.num}
                  />
                </td>
                <td style={s.td}>
                  <input
                    type="number"
                    min="1"
                    defaultValue={p.max_tokens ?? ''}
                    onBlur={(e) =>
                      e.target.value && saveConfig(p, 'max_tokens', Number(e.target.value))
                    }
                    style={s.num}
                  />
                </td>
                <td style={s.td}>v{p.version}</td>
                <td style={s.td}>{p.length} car.</td>
                <td style={s.td}>
                  <button onClick={() => openEditor(p)} style={s.btn}>
                    Éditer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editing && (
        <div style={s.overlay} onClick={() => setEditing(null)}>
          <div style={s.modal} onClick={(e) => e.stopPropagation()}>
            <div style={s.modalHead}>
              <h2 style={s.modalTitle}>{editing.nom_prompt}</h2>
              <button onClick={() => setEditing(null)} style={s.close}>
                ✕
              </button>
            </div>

            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              style={s.textarea}
              spellCheck={false}
            />

            <div style={s.modalFoot}>
              <span style={s.msg}>{message}</span>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => setEditing(null)} style={s.btnGhost}>
                  Annuler
                </button>
                <button onClick={savePrompt} style={s.btnPrimary} disabled={saving}>
                  {saving ? 'Enregistrement…' : 'Enregistrer'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  h1: { margin: '0 0 8px', fontSize: 24 },
  hint: { margin: '0 0 24px', color: '#64748b', fontSize: 13, maxWidth: 680 },
  panel: { background: '#fff', borderRadius: 10, border: '1px solid #e2e8f0', overflow: 'hidden' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 14 },
  th: {
    textAlign: 'left', padding: '12px 16px', background: '#f1f5f9',
    color: '#475569', fontWeight: 600, fontSize: 13,
  },
  td: { padding: '12px 16px', borderTop: '1px solid #f1f5f9', verticalAlign: 'top' },
  preview: {
    color: '#94a3b8', fontSize: 12, marginTop: 4, maxWidth: 340,
    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
  },
  select: { padding: '5px 8px', border: '1px solid #cbd5e1', borderRadius: 5, fontSize: 13 },
  num: { width: 80, padding: '5px 8px', border: '1px solid #cbd5e1', borderRadius: 5, fontSize: 13 },
  btn: {
    padding: '5px 12px', fontSize: 13, border: '1px solid #cbd5e1',
    background: '#fff', borderRadius: 5, cursor: 'pointer',
  },
  overlay: {
    position: 'fixed', inset: 0, background: 'rgba(15,23,42,.6)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50,
  },
  modal: {
    background: '#fff', borderRadius: 12, width: '80vw', maxWidth: 900,
    height: '80vh', display: 'flex', flexDirection: 'column', padding: 24,
  },
  modalHead: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  modalTitle: { margin: 0, fontSize: 18 },
  close: { background: 'none', border: 'none', fontSize: 20, cursor: 'pointer', color: '#64748b' },
  textarea: {
    flex: 1, marginTop: 16, padding: 14, fontFamily: 'monospace', fontSize: 13,
    border: '1px solid #cbd5e1', borderRadius: 8, resize: 'none', lineHeight: 1.5,
  },
  modalFoot: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16,
  },
  msg: { fontSize: 13, color: '#475569' },
  btnGhost: {
    padding: '9px 18px', border: '1px solid #cbd5e1', background: '#fff',
    borderRadius: 6, cursor: 'pointer', fontSize: 14,
  },
  btnPrimary: {
    padding: '9px 18px', border: 'none', background: '#2f73f2', color: '#fff',
    borderRadius: 6, cursor: 'pointer', fontSize: 14,
  },
};