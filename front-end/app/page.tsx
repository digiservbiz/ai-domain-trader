import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-[calc(100vh-3.5rem)] gap-6 p-8 text-center">
      <h1 className="text-5xl font-bold tracking-tight">AI Domain Trader</h1>
      <p className="text-slate-400 max-w-md text-lg">
        Discover undervalued domains with AI-powered trend analysis and valuation.
      </p>
      <div className="flex gap-3 flex-wrap justify-center mt-2">
        <Link
          href="/deals"
          className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold hover:bg-indigo-500 transition-colors"
        >
          Browse Live Deals
        </Link>
        <Link
          href="/search"
          className="rounded-lg bg-slate-700 px-6 py-3 font-semibold hover:bg-slate-600 transition-colors"
        >
          Search Domains
        </Link>
      </div>
      <p className="text-slate-500 text-sm mt-2">
        New here?{' '}
        <Link href="/register" className="text-indigo-400 hover:text-indigo-300">
          Create a free account
        </Link>
      </p>
    </main>
  )
}
