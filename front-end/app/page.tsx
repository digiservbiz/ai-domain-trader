import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-4xl font-bold tracking-tight">AI Domain Trader</h1>
      <p className="text-slate-400 text-center max-w-md">
        Discover undervalued domains using AI-powered trend analysis and valuation.
      </p>
      <div className="flex gap-3">
        <Link
          href="/deals"
          className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold hover:bg-indigo-500 transition-colors"
        >
          View Live Deals
        </Link>
        <Link
          href="/search"
          className="rounded-lg bg-slate-700 px-6 py-3 font-semibold hover:bg-slate-600 transition-colors"
        >
          Search Domains
        </Link>
        <Link
          href="/portfolio"
          className="rounded-lg bg-slate-700 px-6 py-3 font-semibold hover:bg-slate-600 transition-colors"
        >
          Portfolio
        </Link>
        <Link
          href="/snipe"
          className="rounded-lg bg-slate-700 px-6 py-3 font-semibold hover:bg-slate-600 transition-colors"
        >
          Sniper
        </Link>
        <Link
          href="/login"
          className="rounded-lg border border-slate-600 px-6 py-3 font-semibold hover:bg-slate-800 transition-colors"
        >
          Sign in
        </Link>
      </div>
      <p className="text-slate-500 text-sm">
        New here?{' '}
        <Link href="/register" className="text-indigo-400 hover:text-indigo-300">
          Create a free account
        </Link>
      </p>
    </main>
  )
}
