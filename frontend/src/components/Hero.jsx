import React, {useState} from 'react'
import { postPredict } from '../lib/api'

// accept onResult callback to lift results to parent
const CASTE_OPTIONS = ["GOPEN","GOBC","GSCS","GST","EWS","TFWS"]
const SAMPLE_BRANCHES = ["Computer Science and Engineering","Information Technology","AI/ML"]
const SAMPLE_DISTRICTS = ["Amravati","Nagpur","Pune","Mumbai"]

export default function Hero({onResult}){
  const [percentage, setPercentage] = useState('')
  const [caste, setCaste] = useState('GOPEN')
  const [branches, setBranches] = useState([])
  const [districts, setDistricts] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  function toggleItem(listSetter, list, value){
    if(list.includes(value)) listSetter(list.filter(i=>i!==value))
    else listSetter([...list, value])
  }

  async function handleSubmit(e){
    e.preventDefault()
    setError(null)
    setResult(null)
    setLoading(true)
    try{
      const payload = {
        diploma_percentage: parseFloat(percentage),
        caste_category: caste,
        preferred_branches: branches,
        district_filters: districts,
        top_k: 50
      }
      const res = await postPredict(payload)
      setResult(res)
      if(onResult) onResult(res)
    }catch(err){
      console.error(err)
      setError(err.message)
    }finally{
      setLoading(false)
    }
  }

  return (
    <section className="mt-16">
      <div className="max-w-6xl mx-auto px-6">
        <h1 className="text-4xl md:text-5xl font-sans font-extrabold">Predict Your DSE Engineering Admission With <span className="serif-italic text-accent">Data-Driven Precision.</span></h1>
        <p className="mt-3 text-gray-300">Enter your profile to generate confidence-ranked college/branch options.</p>

        <form onSubmit={handleSubmit} className="mt-8 bg-white/4 border border-white/6 rounded-xl p-6 backdrop-blur-md">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-gray-300">Diploma Final Year Percentage</label>
              <input type="number" step="0.01" min="0" max="100" value={percentage} onChange={e=>setPercentage(e.target.value)} className="mt-2 w-full rounded-md px-3 py-2 bg-[#08121a] border border-white/6 text-white" placeholder="e.g., 85.50" />
            </div>

            <div>
              <label className="block text-sm text-gray-300">Caste Category</label>
              <select value={caste} onChange={e=>setCaste(e.target.value)} className="mt-2 w-full rounded-md px-3 py-2 bg-[#08121a] border border-white/6 text-white">
                {CASTE_OPTIONS.map(c=> <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-300">District Filters</label>
              <div className="mt-2 flex gap-2 flex-wrap">
                {SAMPLE_DISTRICTS.map(d=> (
                  <button type="button" key={d} onClick={()=>toggleItem(setDistricts, districts, d)} className={`px-3 py-1 rounded-full text-sm ${districts.includes(d)? 'bg-[var(--accent)] text-black' : 'bg-white/6 text-gray-200'}`}>
                    {d}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm text-gray-300">Preferred Branches</label>
            <div className="mt-2 flex gap-2 flex-wrap">
              {SAMPLE_BRANCHES.map(b=> (
                <button type="button" key={b} onClick={()=>toggleItem(setBranches, branches, b)} className={`px-3 py-1 rounded-full text-sm ${branches.includes(b)? 'bg-[var(--accent)] text-black' : 'bg-white/6 text-gray-200'}`}>
                  {b}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 flex items-center gap-4">
            <button type="submit" className="px-6 py-3 rounded-md bg-[var(--accent)] text-black font-semibold" disabled={loading}>{loading? 'Generating...' : 'Generate Predictive Options'}</button>
            {error && <div className="text-sm text-red-400">{error}</div>}
            {result && <div className="text-sm text-green-300">Results: Dream {result.dream.length}, Realistic {result.realistic.length}, Safe {result.safe.length}</div>}
          </div>
        </form>
      </div>
    </section>
  )
}
