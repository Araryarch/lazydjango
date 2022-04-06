'use client'

import { useState } from 'react'
import { Cog, Play } from 'lucide-react'

interface MiddlewareCreatorProps {
  apiUrl: string
  projectPath: string
  onSuccess?: () => void
}

const MIDDLEWARE_TYPES = ['logging', 'auth', 'rate_limit', 'cors', 'custom']

export default function MiddlewareCreator({ apiUrl, projectPath, onSuccess }: MiddlewareCreatorProps) {
  const [middlewareName, setMiddlewareName] = useState('')
  const [middlewareType, setMiddlewareType] = useState('logging')
  const [customCode, setCustomCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)

  const createMiddleware = async () => {
    if (!middlewareName) {
      setResult({ success: false, message: 'Middleware name is required' })
      return
    }
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch(`${apiUrl}/api/middleware/create/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ middleware_name: middlewareName, middleware_type: middlewareType, custom_code: customCode, project_path: projectPath })
      })
      const data = await res.json()
      setResult(data)
      if (data.success) {
        setMiddlewareName('')
        setCustomCode('')
        onSuccess?.()
      }
    } catch (e) {
      setResult({ success: false, message: 'Failed to connect to API' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4 pb-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <Cog className="w-5 h-5" style={{ color: 'var(--accent)' }} />
        <span className="text-sm tracking-wider font-bold">CREATE MIDDLEWARE</span>
      </div>

      <div className="mb-4">
        <label className="block text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>MIDDLEWARE NAME</label>
        <input type="text" value={middlewareName} onChange={(e) => setMiddlewareName(e.target.value)} placeholder="MyMiddleware" className="w-full" />
      </div>

      <div className="mb-4">
        <label className="block text-xs tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>TYPE</label>
        <div className="grid grid-cols-5 gap-2">
          {MIDDLEWARE_TYPES.map(t => (
            <button key={t} onClick={() => setMiddlewareType(t)} style={{ background: middlewareType === t ? 'var(--accent)' : 'transparent', color: middlewareType === t ? 'var(--bg)' : 'var(--text-secondary)', borderColor: middlewareType === t ? 'var(--accent)' : 'var(--border)' }} className="px-3 py-2 text-xs border">
              {t.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {middlewareType === 'custom' && (
        <div className="mb-4">
          <label className="block text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>CUSTOM CODE</label>
          <textarea value={customCode} onChange={(e) => setCustomCode(e.target.value)} className="w-full h-32 font-mono" placeholder="def my_middleware(get_response): ..." />
        </div>
      )}

      <button onClick={createMiddleware} disabled={loading} className="flex items-center gap-2 text-sm font-bold" style={{ background: 'var(--accent)', color: 'var(--bg)' }}>
        <Play className="w-4 h-4" />
        {loading ? 'CREATING...' : 'CREATE MIDDLEWARE'}
      </button>

      {result && (
        <div className="border mt-4 p-4" style={{ borderColor: result.success ? 'var(--success)' : 'var(--error)' }}>
          <span style={{ color: result.success ? 'var(--success)' : 'var(--error)' }}>{result.message}</span>
        </div>
      )}
    </div>
  )
}
