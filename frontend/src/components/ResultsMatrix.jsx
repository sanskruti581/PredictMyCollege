import React, {useState} from 'react'

export default function ResultsMatrix({result, onAdd}){
  const [tab, setTab] = useState('dream')
  if(!result) return null

  const zones = {
    dream: {label: 'Dream Zone', icon: '🔴', key: 'dream'},
    realistic: {label: 'Realistic Zone', icon: '🟡', key: 'realistic'},
    safe: {label: 'Safe Zone', icon: '🟢', key: 'safe'},
  }

  const rows = result[tab] || []

  return (
    <section className="max-w-6xl mx-auto px-6 mt-12">
      <div className="flex gap-4 items-center">
        {Object.keys(zones).map(k=> (
          <button key={k} onClick={()=>setTab(k)} className={`px-4 py-2 rounded-md ${tab===k? 'bg-[var(--accent)] text-black' : 'bg-white/6 text-gray-200'}`}>
            <span className="mr-2">{zones[k].icon}</span>{zones[k].label}
          </button>
        ))}
      </div>

      <div className="mt-6 bg-white/4 border border-white/6 rounded-xl overflow-hidden">
        <table className="w-full table-auto">
          <thead className="text-left text-gray-300 text-sm">
            <tr>
              <th className="px-4 py-3">Choice Code</th>
              <th className="px-4 py-3">College Name</th>
              <th className="px-4 py-3">Branch</th>
              <th className="px-4 py-3">Cutoff %</th>
              <th className="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx)=> (
              <tr key={`${r.choice_code}-${idx}`} className="border-t border-white/6">
                <td className="px-4 py-3 text-sm">{r.choice_code}</td>
                <td className="px-4 py-3 text-sm">{r.college_name}</td>
                <td className="px-4 py-3 text-sm">{r.branch_name}</td>
                <td className="px-4 py-3 text-sm">{r.cutoff_percentage ?? '—'}</td>
                <td className="px-4 py-3 text-sm">
                  <button onClick={()=>onAdd && onAdd(r)} className="px-3 py-1 rounded-md bg-white/8 hover:bg-[var(--accent)] hover:text-black">+ Add to Choice List</button>
                </td>
              </tr>
            ))}
            {rows.length===0 && (
              <tr><td colSpan={5} className="px-4 py-6 text-center text-gray-400">No results in this zone.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
