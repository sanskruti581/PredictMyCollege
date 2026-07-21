import React, { useState } from 'react'
import { postPredict } from '../lib/api'
import {
  AVAILABLE_COLLEGES,
  AVAILABLE_BRANCHES,
  AVAILABLE_CITIES,
  AVAILABLE_YEARS,
} from '../lib/parsed_metadata'

const PREDICTION_MODES = [
  { value: 'percentage', label: 'By Percentage' },
  { value: 'rank', label: 'By Rank' },
]

const CATEGORY_OPTIONS = ['OPEN', 'OBC', 'SC', 'ST', 'NT', 'VJ', 'EWS']
const GENDER_OPTIONS = ['Male', 'Female']
const SEAT_TYPE_OPTIONS = ['All Seats (Recommended)', 'State Level', 'Home University']
const ADVANCED_SAFETY_ZONES = [
  { key: 'safe', label: '🟢 Safe' },
  { key: 'moderate', label: '🟡 Moderate' },
  { key: 'ambitious', label: '🟣 Ambitious' },
  { key: 'reach', label: '🔴 Reach' },
]
const GAP_FILTER_OPTIONS = [
  'Gap ≥ 0 (cutoff met)',
  'Gap ≥ -3 (moderate)',
  'Show All',
]

export default function Hero({ onResult }) {
  const [predictionMode, setPredictionMode] = useState('percentage')
  const [metric, setMetric] = useState('')
  const [category, setCategory] = useState('OPEN')
  const [gender, setGender] = useState('Male')
  const [seatType, setSeatType] = useState('All Seats (Recommended)')
  const [defence, setDefence] = useState(false)
  const [pwd, setPwd] = useState(false)
  const [tfws, setTfws] = useState(false)
  const [minority, setMinority] = useState(false)
  const [college, setCollege] = useState('All Colleges')
  const [branch, setBranch] = useState('All Branches')
  const [city, setCity] = useState('All Cities')
  const [dataYear, setDataYear] = useState(AVAILABLE_YEARS[0] ?? '2025 (Latest)')
  const [safetyZones, setSafetyZones] = useState(['safe', 'moderate'])
  const [gapFilter, setGapFilter] = useState('Gap ≥ 0 (cutoff met)')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const branchList = AVAILABLE_BRANCHES.length ? AVAILABLE_BRANCHES : ['Computer Science and Engineering', 'Information Technology', 'AI/ML']
  const collegeList = AVAILABLE_COLLEGES.length ? AVAILABLE_COLLEGES : ['All Colleges']
  const cityList = AVAILABLE_CITIES.length ? AVAILABLE_CITIES : ['All Cities']
  const yearList = AVAILABLE_YEARS.length ? AVAILABLE_YEARS : ['2025 (Latest)']
  const metricLabel = predictionMode === 'percentage' ? 'Your Percentage' : 'Your Rank'
  const metricPlaceholder = predictionMode === 'percentage' ? 'e.g. 92.5' : 'e.g. 5000'

  function toggleZone(zone) {
    setSafetyZones(prev =>
      prev.includes(zone) ? prev.filter(item => item !== zone) : [...prev, zone]
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setResult(null)
    const metricValue = parseFloat(metric)
    if (Number.isNaN(metricValue)) {
      setError('Please enter a valid metric value.')
      return
    }

    setLoading(true)
    try {
      const payload = {
        mode: predictionMode,
        metric_value: metricValue,
        diploma_percentage: predictionMode === 'percentage' ? metricValue : undefined,
        state_merit_rank: predictionMode === 'rank' ? metricValue : undefined,
        category,
        gender,
        seat_type: seatType,
        flags: {
          defence,
          pwd,
        },
        special_seats: {
          tfws,
          minority,
        },
        advanced_filters: {
          college,
          branch,
          city,
          data_year: dataYear,
          safety_zones: safetyZones,
          gap_filter: gapFilter,
        },
        top_k: 50,
      }

      const res = await postPredict(payload)
      setResult(res)
      if (onResult) onResult(res)
    } catch (err) {
      console.error(err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="mt-16">
      <div className="max-w-6xl mx-auto px-6">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-sans font-extrabold">
            Predict Your DSE Engineering Admission With{' '}
            <span className="serif-italic text-accent">Data-Driven Precision.</span>
          </h1>
          <p className="text-gray-300">Complete your profile using premium filters for the most reliable outcome.</p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md">
          <div className="grid gap-4 lg:grid-cols-2">
            <div>
              <label className="block text-sm text-gray-300">Prediction Mode</label>
              <select value={predictionMode} onChange={e => setPredictionMode(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                {PREDICTION_MODES.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-300">{metricLabel}</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={metric}
                onChange={e => setMetric(e.target.value)}
                placeholder={metricPlaceholder}
                className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white"
              />
            </div>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-4">
            <div>
              <label className="block text-sm text-gray-300">Main Category</label>
              <select value={category} onChange={e => setCategory(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                {CATEGORY_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-300">Gender</label>
              <select value={gender} onChange={e => setGender(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                {GENDER_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-300">Seat Type</label>
              <select value={seatType} onChange={e => setSeatType(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                {SEAT_TYPE_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-300">Additional Flags</label>
              <div className="mt-2 flex flex-wrap gap-2">
                <label className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-200">
                  <input type="checkbox" checked={defence} onChange={() => setDefence(prev => !prev)} className="mr-2 h-4 w-4 rounded bg-[#08121a] text-accent" />
                  Defence
                </label>
                <label className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-200">
                  <input type="checkbox" checked={pwd} onChange={() => setPwd(prev => !prev)} className="mr-2 h-4 w-4 rounded bg-[#08121a] text-accent" />
                  PWD
                </label>
              </div>
            </div>
          </div>

          <div className="mt-6">
            <label className="block text-sm text-gray-300">Special Seat Options</label>
            <div className="mt-3 flex flex-wrap gap-3">
              <label className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-200">
                <input type="checkbox" checked={tfws} onChange={() => setTfws(prev => !prev)} className="mr-2 h-4 w-4 rounded bg-[#08121a] text-accent" />
                TFWS
              </label>
              <label className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-200">
                <input type="checkbox" checked={minority} onChange={() => setMinority(prev => !prev)} className="mr-2 h-4 w-4 rounded bg-[#08121a] text-accent" />
                Minority
              </label>
            </div>
          </div>

          <div className="mt-8 rounded-[2rem] border border-dashed border-white/10 bg-white/5 p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-sm font-semibold text-gray-100">🎯 Advanced Filters</div>
              <span className="inline-flex rounded-full bg-white/10 px-3 py-1 text-xs uppercase tracking-[0.18em] text-gray-300">All optional</span>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-4">
              <div>
                <label className="block text-sm text-gray-300">College</label>
                <select value={college} onChange={e => setCollege(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                  <option>All Colleges</option>
                  {collegeList.map(name => (
                    <option key={name} value={name}>{name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-300">Branch</label>
                <select value={branch} onChange={e => setBranch(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                  <option>All Branches</option>
                  {branchList.map(name => (
                    <option key={name} value={name}>{name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-300">City</label>
                <select value={city} onChange={e => setCity(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                  <option>All Cities</option>
                  {cityList.map(name => (
                    <option key={name} value={name}>{name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-300">Data Year</label>
                <select value={dataYear} onChange={e => setDataYear(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                  {yearList.map(name => (
                    <option key={name} value={name}>{name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mt-6">
              <div className="text-sm text-gray-300">Filter by Safety Zone:</div>
              <div className="mt-3 flex flex-wrap gap-3">
                {ADVANCED_SAFETY_ZONES.map(zone => (
                  <button
                    type="button"
                    key={zone.key}
                    onClick={() => toggleZone(zone.key)}
                    className={`rounded-full border px-4 py-2 text-sm transition ${safetyZones.includes(zone.key) ? 'border-accent bg-[var(--accent)] text-black' : 'border-white/10 bg-white/5 text-gray-200'}`}>
                    {zone.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2 sm:items-end">
              <div>
                <label className="block text-sm text-gray-300">Gap Filter</label>
                <select value={gapFilter} onChange={e => setGapFilter(e.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-[#08121a] px-4 py-3 text-white">
                  {GAP_FILTER_OPTIONS.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
              <p className="text-sm text-gray-400">Tip: "Show All" reveals Reach colleges too.</p>
            </div>
          </div>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <button type="submit" className="inline-flex items-center justify-center rounded-2xl bg-[var(--accent)] px-6 py-3 text-sm font-semibold text-black transition hover:brightness-105 disabled:opacity-60" disabled={loading}>
              {loading ? 'Generating...' : 'Generate Predictive Options'}
            </button>
            <div className="space-y-2 text-right">
              {error && <div className="text-sm text-red-400">{error}</div>}
              {result && <div className="text-sm text-emerald-300">Results: Dream {result.dream.length}, Realistic {result.realistic.length}, Safe {result.safe.length}</div>}
            </div>
          </div>
        </form>
      </div>
    </section>
  )
}
