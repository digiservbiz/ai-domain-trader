'use client'
import { useState } from 'react'
import Link from 'next/link'

interface Props {
  domain: string
  estValue: number
  score: number
}

interface Availability {
  available: boolean
  price: number
  currency: string
}

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export default function DealCard({ domain, estValue, score }: Props) {
  const [availability, setAvailability] = useState<Availability | null>(null)
  const [checking, setChecking] = useState(false)
  const [listPrice, setListPrice] = useState(String(Math.round(estValue)))
  const [listing, setListing] = useState(false)
  const [listed, setListed] = useState(false)
  const [error, setError] = useState('')

  const scoreColor = score >= 70 ? 'bg-green-500' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500'

  async function checkAvailability() {
    setChecking(true)
    setError('')
    try {
      const res = await fetch(`${API}/domains/${domain}/check`)
      if (!res.ok) throw new Error('Check failed')
      setAvailability(await res.json())
    } catch {
      setError('Could not check availability')
    } finally {
      setChecking(false)
    }
  }

  async function listForSale() {
    setListing(true)
    setError('')
    try {
      const res = await fetch(`${API}/domains/${domain}/list`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ price: parseFloat(listPrice) }),
      })
      if (res.status === 401) { setError('__login__'); return }
      if (!res.ok) throw new Error('Listing failed')
      setListed(true)
    } catch {
      setError('Could not list domain')
    } finally {
      setListing(false)
    }
  }

  return (
    <div className="rounded-xl bg-slate-800 border border-slate-700 p-4 space-y-3">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <span className="font-mono font-semibold text-white truncate">{domain}</span>
        <span className="text-yellow-400 font-semibold whitespace-nowrap text-sm">
          ${estValue.toLocaleString()}
        </span>
      </div>

      {/* Score bar */}
      <div className="space-y-1">
        <div className="flex justify-between text-xs text-slate-400">
          <span>Trend score</span>
          <span>{score}</span>
        </div>
        <div className="h-1.5 rounded-full bg-slate-700 overflow-hidden">
          <div className={`h-full rounded-full ${scoreColor}`} style={{ width: `${score}%` }} />
        </div>
      </div>

      {/* Availability result */}
      {availability && (
        <div className={`flex items-center gap-2 text-sm rounded-lg px-3 py-2 ${
          availability.available ? 'bg-green-900/40 text-green-300' : 'bg-red-900/40 text-red-300'
        }`}>
          <span>{availability.available ? '✓ Available' : '✗ Already taken'}</span>
          {availability.available && availability.price > 0 && (
            <span className="ml-auto text-xs opacity-70">
              Reg. {availability.currency} {(availability.price / 1_000_000).toFixed(2)}
            </span>
          )}
        </div>
      )}

      {/* List for sale form */}
      {availability?.available && !listed && (
        <div className="flex gap-2">
          <div className="relative flex-1">
            <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
            <input
              type="number"
              min="1"
              value={listPrice}
              onChange={e => setListPrice(e.target.value)}
              className="w-full rounded-lg bg-slate-700 border border-slate-600 pl-6 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            onClick={listForSale}
            disabled={listing}
            className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold hover:bg-indigo-500 transition-colors disabled:opacity-50 whitespace-nowrap"
          >
            {listing ? 'Listing…' : 'List for sale'}
          </button>
        </div>
      )}

      {/* Success state */}
      {listed && (
        <p className="text-green-400 text-sm text-center">✓ Listed on GoDaddy</p>
      )}

      {/* Error / login prompt */}
      {error === '__login__' ? (
        <p className="text-sm text-slate-400 text-center">
          <Link href="/login" className="text-indigo-400 hover:text-indigo-300">Sign in</Link>
          {' '}to list this domain
        </p>
      ) : error ? (
        <p className="text-red-400 text-sm">{error}</p>
      ) : null}

      {/* Check button */}
      {!availability && (
        <button
          onClick={checkAvailability}
          disabled={checking}
          className="w-full rounded-lg border border-slate-600 px-3 py-2 text-sm font-medium hover:bg-slate-700 transition-colors disabled:opacity-50"
        >
          {checking ? 'Checking…' : 'Check availability'}
        </button>
      )}
    </div>
  )
}
