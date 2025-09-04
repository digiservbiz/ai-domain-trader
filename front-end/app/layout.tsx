import './globals.css'
export const metadata = { title: 'AI Domain Trader' }
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang='en'><body className='bg-slate-900 text-white'>{children}</body></html>
}
