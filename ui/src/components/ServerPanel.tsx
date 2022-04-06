'use client'

import { useState } from 'react'
import { Server, Play, CheckCircle, XCircle, Terminal } from 'lucide-react'

interface ServerPanelProps {
  apiUrl: string
  projectPath: string
}

type Command = 'start' | 'migrate' | 'check' | 'shell'

const COMMANDS: { value: Command; label: string; desc: string }[] = [
  { value: 'check', label: 'CHECK', desc: 'Django checks' },
  { value: 'migrate', label: 'MIGRATE', desc: 'DB migrations' },
  { value: 'start', label: 'START', desc: 'Dev server' },
  { value: 'shell', label: 'SHELL', desc: 'Django shell' },
]

export default function ServerPanel({ apiUrl, projectPath }: ServerPanelProps) {
  const [command, setCommand] = useState<Command>('check')
  const [app, setApp] = useState('')
  const [port, setPort] = useState(8000)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const runCommand = async () => {
    setLoading(true)
    setResult(null)
    try {
      const body: any = { command, project_path: projectPath }
      if (command === 'migrate' && app) body.app = app
      if (command === 'start') { body.port = port; body.host = '0.0.0.0' }

      const res = await fetch(`${apiUrl}/api/server/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setResult({ success: false, message: 'Failed to connect to API' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4 pb-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <Terminal className="w-5 h-5" style={{ color: 'var(--accent)' }} />
        <span className="text-sm tracking-wider font-bold">SERVER COMMANDS</span>
      </div>

      <div className="mb-4">
        <label className="block text-xs tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>COMMAND</label>
        <div className="grid grid-cols-4 gap-2">
          {COMMANDS.map(c => (
            <button key={c.value} onClick={() => setCommand(c.value)} style={{ background: command === c.value ? 'var(--accent)' : 'transparent', color: command === c.value ? 'var(--bg)' : 'var(--text-secondary)', borderColor: command === c.value ? 'var(--accent)' : 'var(--border)' }} className="px-3 py-3 text-xs border flex flex-col items-center">
              <span className="font-bold">{c.label}</span>
              <span style={{ color: command === c.value ? 'var(--bg)' : 'var(--text-muted)' }} className="mt-1">{c.desc}</span>
            </button>
          ))}
        </div>
      </div>

      {command === 'migrate' && (
        <div className="mb-4">
          <label className="block text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>APP (OPTIONAL)</label>
          <input type="text" value={app} onChange={(e) => setApp(e.target.value)} placeholder="myapp" className="w-48" />
        </div>
      )}

      {command === 'start' && (
        <div className="mb-4">
          <label className="block text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>PORT</label>
          <input type="number" value={port} onChange={(e) => setPort(parseInt(e.target.value) || 8000)} className="w-32" />
        </div>
      )}

      <button onClick={runCommand} disabled={loading} className="flex items-center gap-2 text-sm font-bold" style={{ background: 'var(--accent)', color: 'var(--bg)' }}>
        <Play className="w-4 h-4" />
        {loading ? 'RUNNING...' : 'RUN'}
      </button>

      {result && (
        <div className="border mt-4" style={{ borderColor: result.success ? 'var(--success)' : 'var(--error)' }}>
          <div className="flex items-center gap-2 px-4 py-2" style={{ background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border)' }}>
            {result.success ? <CheckCircle className="w-4 h-4" style={{ color: 'var(--success)' }} /> : <XCircle className="w-4 h-4" style={{ color: 'var(--error)' }} />}
            <span style={{ color: result.success ? 'var(--success)' : 'var(--error)' }}>{result.message}</span>
          </div>
          {result.data?.output && (
            <pre className="p-4 text-xs font-mono overflow-auto max-h-64" style={{ background: 'var(--bg)', color: 'var(--accent)' }}>
              {result.data.output}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
