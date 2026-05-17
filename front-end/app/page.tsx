import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-4xl font-bold tracking-tight">AI Domain Trader</h1>
      <p className="text-slate-400 text-center max-w-md">
        Discover undervalued domains using AI-powered trend analysis and valuation.
      </p>
      <Link
        href="/deals"
        className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold hover:bg-indigo-500 transition-colors"
      >
        View Live Deals
      </Link>
    </main>
  )
}
