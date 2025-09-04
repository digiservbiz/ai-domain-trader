'use client'
import useSWRSubscription from 'swr/subscription'
export default function LiveDeals() {
  const { data } = useSWRSubscription('ws://localhost:8000/ws/deals', (k,{next})=>{
    const s=new WebSocket(k); s.onmessage=e=>next(null,JSON.parse(e.data)); return ()=>s.close()
  })
  return <ul>{data?.map((d:any)=><li key={d.domain}>{d.domain} –  – Score {d.score}</li>)}</ul>
}
