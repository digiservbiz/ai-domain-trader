'use client'
import useSWRSubscription from 'swr/subscription'
import DealCard from '@/components/DealCard'

interface Deal {
  domain: string
  score: number
  estValue: number
}

export default function LiveDeals() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
  const wsUrl = apiUrl.replace(/^http/, 'ws') + '/ws/deals'

  const { data, error } = useSWRSubscription(
    wsUrl,
    (key, { next }) => {
      const ws = new WebSocket(key)
      ws.onmessage = (e) => next(null, JSON.parse(e.data) as Deal[])
      ws.onerror = () => next(new Error('WebSocket error'))
      return () => ws.close()
    }
  )

  if (error) return <p className="max-w-6xl mx-auto px-4 py-12 text-red-400">Failed to connect: {error.message}</p>
  if (!data) return <p className="max-w-6xl mx-auto px-4 py-12 text-slate-400">Connecting to live deals…</p>
  if (data.length === 0) return <p className="max-w-6xl mx-auto px-4 py-12 text-slate-400">No deals available yet.</p>

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold">Live Domain Deals</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data.map((d: Deal) => (
          <DealCard key={d.domain} domain={d.domain} score={d.score} estValue={d.estValue} />
        ))}
      </div>
    </div>
  )
}
