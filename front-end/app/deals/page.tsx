'use client'
import useSWRSubscription from 'swr/subscription'

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

  if (error) return <p className="p-4 text-red-400">Failed to connect: {error.message}</p>
  if (!data) return <p className="p-4 text-slate-400">Connecting to live deals...</p>
  if (data.length === 0) return <p className="p-4 text-slate-400">No deals available yet.</p>

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Live Domain Deals</h1>
      <ul className="space-y-2">
        {data.map((d: Deal) => (
          <li
            key={d.domain}
            className="flex items-center justify-between rounded-lg bg-slate-800 px-4 py-3"
          >
            <span className="font-mono text-white">{d.domain}</span>
            <span className="text-slate-300 text-sm">
              Score <span className="text-green-400 font-semibold">{d.score}</span>
              &nbsp;&bull;&nbsp;Est.&nbsp;
              <span className="text-yellow-400 font-semibold">${d.estValue.toLocaleString()}</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
