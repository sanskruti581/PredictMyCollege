import React from 'react'

export default function CapFormBuilder({choiceList, onMoveUp, onMoveDown, onRemove}){
  const maxChoices = 300

  return (
    <section className="max-w-6xl mx-auto px-6 mt-8">
      <div className="bg-white/4 border border-white/6 rounded-xl p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">CAP Choice Builder</h3>
          <div className="text-sm text-gray-300">{choiceList.length} / {maxChoices} Choices Confirmed</div>
        </div>

        <div className="mt-4">
          {choiceList.length===0 && <div className="text-gray-400">No choices added yet. Use the Results Matrix to add.</div>}

          <ol className="mt-2 space-y-2">
            {choiceList.map((c, idx)=> (
              <li key={`${c.choice_code}-${idx}`} className="flex items-center justify-between bg-white/6 p-3 rounded-md">
                <div>
                  <div className="text-sm font-medium">{idx+1}. {c.branch_name} — {c.college_name}</div>
                  <div className="text-xs text-gray-300">Choice: {c.choice_code} • Cutoff: {c.cutoff_percentage ?? '—'}</div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={()=>onMoveUp && onMoveUp(idx)} disabled={idx===0} className="px-2 py-1 bg-white/8 rounded">↑</button>
                  <button onClick={()=>onMoveDown && onMoveDown(idx)} disabled={idx===choiceList.length-1} className="px-2 py-1 bg-white/8 rounded">↓</button>
                  <button onClick={()=>onRemove && onRemove(idx)} className="px-2 py-1 bg-red-600 text-black rounded">Remove</button>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  )
}
