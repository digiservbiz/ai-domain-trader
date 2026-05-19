'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import useSWR from 'swr'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

interface PortfolioItem {
  domain: string
  bought_price: number
  bought_at: string
  current_value: number
  pnl: number
  pnl_pct: number
}

interface PortfolioData {
  items: PortfolioItem[]
  total_invested: number
  total_current: number
  total_pnl: number
}

function fmt(n: number) {
  return '$' + Math.abs(n).toFixed(2)
}

function PnlCell({ pnl, pnl_pct }: { pnl: number; pnl_pct: number }) {
  const pos = pnl >= 0
  const color = pos ? 'text-green-400' : 'text-red-400'
  const sign = pos ? '+' : '-'
  return (
    <span className={color}>
      {sign}{fmt(pnl)} ({sign}{Math.abs(pnl_pct).toFixed(1)}%)
    </span>
  )
}

export default function PortfolioPage() {
  const router = useRouter()
  const [ready, setReady] = useState(false)
  const [domain, setDomain] = useState('')
  const [price, setPrice] = useState('')
  const [addError, setAddError] = useState('')
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    fetch(`${API}/auth/me`, { credentials: 'include' }).then(r => {
      if (r.status === 401) {
        router.push('/login')
      } else {
        setReady(true)
      }
    }).catch(() => router.push('/login'))
  }, [router])

  const fetcher = (url: string) =>
    fetch(url, { credentials: 'include' }).then((r) => {
      if (!r.ok) throw new Error('Failed to fetch portfolio')
      return r.json()
    })

  const { data, error, mutate } = useSWR<PortfolioData>(
    ready ? `${API}/portfolio` : null,
    fetcher
  )

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    if (!domain.trim() || !price) return
    setAdding(true)
    setAddError('')
    try {
      const res = await fetch(`${API}/portfolio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ domain: domain.trim(), bought_price: parseFloat(price) }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        setAddError(body.detail ?? 'Domain already in portfolio or invalid.')
      } else {
        setDomain('')
        setPrice('')
        mutate()
      }
    } catch {
      setAddError('Network error. Please try again.')
    } finally {
      setAdding(false)
    }
  }

  async function handleRemove(d: string) {
    await fetch(`${API}/portfolio/${encodeURIComponent(d)}`, {
      method: 'DELETE',
      credentials: 'include',
    })
    mutate()
  }

  if (!ready) return null

  const totalPnl = data?.total_pnl ?? 0
  const pnlPos = totalPnl >= 0
  const pnlColor = pnlPos ? 'text-green-400' : 'text-red-400'
  const pnlSign = pnlPos ? '+' : '-'
  const pnlPct =
    data && data.total_invested > 0
      ? (Math.abs(totalPnl) / data.total_invested) * 100
      : 0

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold">My Portfolio</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-slate-800 rounded-lg p-4">
          <p className="text-slate-400 text-sm mb-1">Total Invested</p>
          <p className="text-xl font-semibold">{fmt(data?.total_invested ?? 0)}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4">
          <p className="text-slate-400 text-sm mb-1">Current Value</p>
          <p className="text-xl font-semibold">{fmt(data?.total_current ?? 0)}</p>
        </div>
        <div className="bg-slate-800 rounded-lg p-4">
          <p className="text-slate-400 text-sm mb-1">Total P&amp;L</p>
          <p className={`text-xl font-semibold ${pnlColor}`}>
            {pnlSign}{fmt(totalPnl)} ({pnlSign}{pnlPct.toFixed(1)}%)
          </p>
        </div>
      </div>

      <form onSubmit={handleAdd} className="flex flex-wrap gap-3 items-start">
        <input
          type="text"
          placeholder="myniche.com"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          className="flex-1 min-w-[180px] rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <input
          type="number"
          placeholder="Bought price ($)"
          value={price}
          min="0"
          step="0.01"
          onChange={(e) => setPrice(e.target.value)}
          className="w-44 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          disabled={adding || !domain.trim() || !price}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold hover:bg-indigo-500 disabled:opacity-50 transition-colors"
        >
          {adding ? 'Adding…' : 'Add to portfolio'}
        </button>
        {addError && <p className="w-full text-sm text-red-400">{addError}</p>}
      </form>

      {error && <p className="text-red-400 text-sm">Failed to load portfolio.</p>}

      {!data && !error && <p className="text-slate-400">Loading portfolio…</p>}

      {data && (
        <div className="overflow-x-auto">
          {data.items.length === 0 ? (
            <p className="text-slate-400 text-sm">No domains in portfolio yet. Add one above.</p>
          ) : (
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="text-slate-400 border-b border-slate-700">
                  <th className="text-left py-2 pr-4">Domain</th>
                  <th className="text-right py-2 pr-4">Bought</th>
                  <th className="text-right py-2 pr-4">Current Value</th>
                  <th className="text-right py-2 pr-4">P&amp;L</th>
                  <th className="text-right py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((item) => (
                  <tr key={item.domain} className="border-b border-slate-800 hover:bg-slate-800/40">
                    <td className="py-3 pr-4 font-medium">{item.domain}</td>
                    <td className="py-3 pr-4 text-right text-slate-300">{fmt(item.bought_price)}</td>
                    <td className="py-3 pr-4 text-right text-slate-300">{fmt(item.current_value)}</td>
                    <td className="py-3 pr-4 text-right">
                      <PnlCell pnl={item.pnl} pnl_pct={item.pnl_pct} />
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleRemove(item.domain)}
                        className="text-xs text-red-400 hover:text-red-300 border border-red-900 rounded px-2 py-1 hover:bg-red-950 transition-colors"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}
