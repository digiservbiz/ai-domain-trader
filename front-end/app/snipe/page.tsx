'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import useSWR from 'swr'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

type SnipeTarget = {
  id: number
  domain: string
  max_bid: number
  status: string
  current_bid: number | null
  last_checked: string | null
  created_at: string
}

function getToken() {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem('token') ?? ''
}

function fetcher(url: string) {
  const token = getToken()
  return fetch(url, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json())
}

function relativeTime(iso: string | null) {
  if (!iso) return 'Never'
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

const statusStyles: Record<string, string> = {
  watching: 'bg-slate-700 text-slate-300',
  bid_placed: 'bg-blue-900 text-blue-300',
  won: 'bg-green-900 text-green-300',
  lost: 'bg-red-900 text-red-300',
  outbid: 'bg-red-900 text-red-300',
  error: 'bg-orange-900 text-orange-300',
}

export default function SnipePage() {
  const router = useRouter()
  const [domain, setDomain] = useState('')
  const [maxBid, setMaxBid] = useState('')
  const [formError, setFormError] = useState('')
  const [triggered, setTriggered] = useState<Record<string, boolean>>({})

  useEffect(() => {
    if (!localStorage.getItem('token')) router.push('/login')
  }, [router])

  const { data: targets, isLoading, mutate } = useSWR<SnipeTarget[]>(
    `${API}/snipe`,
    fetcher,
    { refreshInterval: 30000 }
  )

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    setFormError('')
    const token = getToken()
    const res = await fetch(`${API}/snipe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ domain: domain.trim(), max_bid: parseFloat(maxBid) }),
    })
    if (res.status === 409 || res.status === 400) {
      const body = await res.json().catch(() => ({}))
      setFormError(body.detail ?? 'Domain already being watched.')
      return
    }
    if (!res.ok) {
      setFormError('Failed to add target.')
      return
    }
    setDomain('')
    setMaxBid('')
    mutate()
  }

  async function handleRemove(d: string) {
    const token = getToken()
    await fetch(`${API}/snipe/${encodeURIComponent(d)}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    mutate()
  }

  async function handleTrigger(d: string) {
    const token = getToken()
    await fetch(`${API}/snipe/${encodeURIComponent(d)}/trigger`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    setTriggered(prev => ({ ...prev, [d]: true }))
    setTimeout(() => setTriggered(prev => ({ ...prev, [d]: false })), 3000)
  }

  return (
    <main className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Auction Sniper</h1>
          <p className="text-slate-400 mt-1">
            Automatically bid on GoDaddy auctions when price drops below your max.
          </p>
        </div>

        <form onSubmit={handleAdd} className="flex flex-wrap gap-3 items-start">
          <div className="flex flex-col gap-1">
            <input
              type="text"
              value={domain}
              onChange={e => setDomain(e.target.value)}
              placeholder="domain.com"
              required
              className="rounded-lg bg-slate-800 border border-slate-700 px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 w-56"
            />
          </div>
          <div className="flex flex-col gap-1">
            <input
              type="number"
              value={maxBid}
              onChange={e => setMaxBid(e.target.value)}
              placeholder="Max bid ($)"
              required
              min="1"
              step="0.01"
              className="rounded-lg bg-slate-800 border border-slate-700 px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 w-36"
            />
          </div>
          <button
            type="submit"
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold hover:bg-indigo-500 transition-colors"
          >
            Watch domain
          </button>
          {formError && <p className="w-full text-sm text-red-400">{formError}</p>}
        </form>

        {isLoading ? (
          <p className="text-slate-400">Loading targets…</p>
        ) : !targets || targets.length === 0 ? (
          <p className="text-slate-400">
            No snipe targets yet. Add a domain above to start watching auctions.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-slate-700">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 text-slate-400 text-left">
                  <th className="px-4 py-3 font-medium">Domain</th>
                  <th className="px-4 py-3 font-medium">Max Bid</th>
                  <th className="px-4 py-3 font-medium">Current Bid</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Last Checked</th>
                  <th className="px-4 py-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {targets.map(t => (
                  <tr key={t.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                    <td className="px-4 py-3 font-medium">{t.domain}</td>
                    <td className="px-4 py-3">${t.max_bid.toFixed(2)}</td>
                    <td className="px-4 py-3">
                      {t.current_bid != null ? `$${t.current_bid.toFixed(2)}` : '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          statusStyles[t.status] ?? 'bg-slate-700 text-slate-300'
                        }`}
                      >
                        {t.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{relativeTime(t.last_checked)}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleTrigger(t.domain)}
                          className="rounded bg-slate-700 px-3 py-1 text-xs font-medium hover:bg-slate-600 transition-colors"
                        >
                          {triggered[t.domain] ? 'Triggered!' : 'Snipe Now'}
                        </button>
                        <button
                          onClick={() => handleRemove(t.domain)}
                          className="rounded bg-red-900/60 px-3 py-1 text-xs font-medium hover:bg-red-800 transition-colors text-red-300"
                        >
                          Remove
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  )
}
