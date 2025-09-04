type Props={domain:string;estValue:number;score:number}
export default function DealCard({domain,estValue,score}:Props){
  return <div className='border rounded p-4 bg-slate-800'><h2>{domain}</h2><p></p><p>{score}</p></div>
}
