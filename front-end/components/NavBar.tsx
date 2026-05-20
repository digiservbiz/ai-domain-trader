'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

const links = [
  { href: '/deals', label: 'Live Deals' },
  { href: '/search', label: 'Search' },
  { href: '/portfolio', label: 'Portfolio' },
  { href: '/snipe', label: 'Sniper' },
]

export default function NavBar() {
  const router = useRouter()
  const pathname = usePathname()
  const [authed, setAuthed] = useState<boolean | null>(null)

  useEffect(() => {
    fetch(`${API}/auth/me`, { credentials: 'include' })
      .then(r => setAuthed(r.ok))
      .catch(() => setAuthed(false))
  }, [pathname])

  async function signOut() {
    await fetch(`${API}/auth/logout`, { method: 'POST', credentials: 'include' })
    setAuthed(false)
    router.push('/')
  }

  return (
    <header className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur border-b border-slate-800">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-6">
        <Link href="/" className="font-bold text-white tracking-tight shrink-0">
          AI Domain Trader
        </Link>
        <nav className="flex items-center gap-1 flex-1 overflow-x-auto">
          {links.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`px-3 py-1.5 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
                pathname.startsWith(href)
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="shrink-0 min-w-[70px] flex justify-end">
          {authed === true && (
            <button
              onClick={signOut}
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              Sign out
            </button>
          )}
          {authed === false && (
            <Link
              href="/login"
              className="rounded-lg bg-indigo-600 px-4 py-1.5 text-sm font-semibold hover:bg-indigo-500 transition-colors"
            >
              Sign in
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}
