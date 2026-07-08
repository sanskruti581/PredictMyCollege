const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function postPredict(payload){
  const url = `${API_BASE}/predict`
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if(!res.ok){
    const txt = await res.text()
    throw new Error(`API error ${res.status}: ${txt}`)
  }
  return res.json()
}
