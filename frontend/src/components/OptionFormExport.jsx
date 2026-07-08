import React from 'react'

function openPrintWindow(html){
  const w = window.open('', '_blank')
  if(!w) return
  w.document.write(html)
  w.document.close()
  w.focus()
  w.print()
}

export default function OptionFormExport({choiceList}){
  function handleExport(){
    const rowsHtml = choiceList.map((c, i)=> `
      <tr>
        <td style="padding:6px;border:1px solid #ddd">${i+1}</td>
        <td style="padding:6px;border:1px solid #ddd">${c.choice_code}</td>
        <td style="padding:6px;border:1px solid #ddd">${c.college_name}</td>
        <td style="padding:6px;border:1px solid #ddd">${c.branch_name}</td>
      </tr>
    `).join('\n')

    const html = `
      <html><head><title>CAP Preference Cheat-Sheet</title>
      <style>body{font-family: Arial; background:white; color:#111} table{border-collapse:collapse;width:100%}</style>
      </head><body>
      <h2>CAP Preference Cheat-Sheet</h2>
      <table>
        <thead><tr><th style="padding:6px;border:1px solid #ddd">#</th><th style="padding:6px;border:1px solid #ddd">Choice Code</th><th style="padding:6px;border:1px solid #ddd">College</th><th style="padding:6px;border:1px solid #ddd">Branch</th></tr></thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>
      </body></html>
    `

    openPrintWindow(html)
  }

  return (
    <section className="max-w-6xl mx-auto px-6 mt-6">
      <div className="flex items-center justify-between bg-white/4 border border-white/6 rounded-xl p-4">
        <div>
          <h4 className="font-semibold">Review & Export</h4>
          <p className="text-sm text-gray-300">Finalize your preference order and download a printable cheat-sheet matching the CAP layout.</p>
        </div>
        <div>
          <button onClick={handleExport} className="px-4 py-2 rounded-md bg-[var(--accent)] text-black font-semibold">Download Preference Cheat-Sheet PDF</button>
        </div>
      </div>
    </section>
  )
}
