// En dev et avec docker compose, /api est servi sur la même origine (proxy).
// Pour un front hébergé ailleurs (Vercel), définir VITE_API_URL=https://votre-api.example.com
const BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

async function appel(chemin, options) {
  const res = await fetch(`${BASE}${chemin}`, options)
  if (!res.ok) throw new Error(`API ${res.status}`)
  return res.json()
}

export const getInfo = () => appel('/api/info')

export const predict = (text) =>
  appel('/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
