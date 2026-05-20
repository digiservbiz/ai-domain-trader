'use client'

import { useState, useEffect, useCallback } from 'react'
import useSWR from 'swr'
import DealCard from '@/components/DealCard'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

interface DomainItem {
  domain: string
  score: number
  estValue: number
}

interface ApiResponse {
  items: DomainItem[]
  total: number
  page: number
  pages: number
}

function buildQuery(q: string, tld: string, minScore: string, maxValue: string, page: number) {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (tld) params.set('tld', tld)
  if (minScore) params.set('min_score', minScore)
  if (maxValue) params.set('max_value', maxValue)
  params.set('page', String(page))
  params.set('limit', '12')
  return params.toString()
}

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function SearchPage() {
  const [q, setQ] = useState('')
  const [tld, setTld] = useState('')
  const [minScore, setMinScore] = useState('')
  const [maxValue, setMaxValue] = useState('')
  const [page, setPage] = useState(1)
  const [debouncedQ, setDebouncedQ] = useState('')
  const [committed, setCommitted] = useState({ tld: '', minScore: '', maxValue: '' })

  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedQ(q)
      setPage(1)
    }, 400)
    return () => clearTimeout(t)
  }, [q])

  const queryString = buildQuery(debouncedQ, committed.tld, committed.minScore, committed.maxValue, page)
  const { data, isLoading } = useSWR<ApiResponse>(`${API}/domains?${queryString}`, fetcher)

  const handleSearch = useCallback(() => {
    setCommitted({ tld, minScore, maxValue })
    setPage(1)
  }, [tld, minScore, maxValue])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch()
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="sticky top-14 z-10 bg-slate-900/95 backdrop-blur border-b border-slate-800 px-4 py-3">
        <div className="max-w-6xl mx-auto flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[180px]">
            <label className="block text-xs text-slate-400 mb-1">Search domains</label>
            <input
              type="text"
              placeholder="Search domains…"
              value={q}
              onChange={e => setQ(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="min-w-[120px]">
            <label className="block text-xs text-slate-400 mb-1">TLD</label>
            <select
              value={tld}
              onChange={e => setTld(e.target.value)}
              className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All TLDs</option>
              <option value=".com">.com</option>
              <option value=".io">.io</option>
              <option value=".ai">.ai</option>
              <option value=".co">.co</option>
              <option value=".net">.net</option>
              <option value=".org">.org</option>
            </select>
          </div>
          <div className="min-w-[100px]">
            <label className="block text-xs text-slate-400 mb-1">Min score</label>
            <input
              type="number"
              min={0}
              max={100}
              placeholder="0"
              value={minScore}
              onChange={e => setMinScore(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="min-w-[120px]">
            <label className="block text-xs text-slate-400 mb-1">Max value $</label>
            <input
              type="number"
              min={0}
              placeholder="Any"
              value={maxValue}
              onChange={e => setMaxValue(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            onClick={handleSearch}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold hover:bg-indigo-500 transition-colors"
          >
            Search
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6">
        {isLoading ? (
          <p className="text-slate-400 text-center py-12">Searching…</p>
        ) : !data || data.items.length === 0 ? (
          <p className="text-slate-400 text-center py-12">No domains found. Try different filters.</p>
        ) : (
          <>
            <p className="text-slate-400 text-sm mb-4">{data.total} domain{data.total !== 1 ? 's' : ''} found</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.items.map(item => (
                <DealCard key={item.domain} domain={item.domain} score={item.score} estValue={item.estValue} />
              ))}
            </div>
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={() => setPage(p => p - 1)}
                disabled={page <= 1}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium hover:bg-slate-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Prev
              </button>
              <span className="text-slate-400 text-sm">Page {data.page} of {data.pages}</span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= data.pages}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium hover:bg-slate-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
