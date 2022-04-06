'use client'

import { useState, useEffect } from 'react'
import { Database, RefreshCw } from 'lucide-react'

interface ProjectInfoProps {
  apiUrl: string
  projectPath: string
}

interface ProjectData {
  success: boolean
  data?: {
    path: string
    name: string
    apps: string[]
    is_django: boolean
  }
  detail?: string
}

export default function ProjectInfo({ apiUrl, projectPath }: ProjectInfoProps) {
  const [data, setData] = useState<ProjectData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchInfo = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${apiUrl}/api/project/?project_path=${encodeURIComponent(projectPath)}`)
      const json = await res.json()
      setData(json)
    } catch (e) {
      setError('Failed to connect to API')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchInfo()
  }, [apiUrl, projectPath])

  if (loading) {
    return (
      <div style={{ color: 'var(--text-secondary)' }}>
        Loading...
      </div>
    )
  }

  if (error || !data?.success) {
    return (
      <div>
        <div className="flex items-center justify-between pb-4 mb-4" style={{ borderBottom: '1px solid var(--border)' }}>
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5" style={{ color: 'var(--accent)' }} />
            <span className="text-sm tracking-wider font-bold">PROJECT INFO</span>
          </div>
          <button
            onClick={fetchInfo}
            className="flex items-center gap-1 text-xs px-2 py-1"
            style={{ color: 'var(--text-muted)' }}
          >
            <RefreshCw className="w-3 h-3" /> RETRY
          </button>
        </div>
        <div style={{ color: 'var(--error)' }} className="text-sm">{error || data?.detail || 'Not a Django project'}</div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4 pb-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <Database className="w-5 h-5" style={{ color: 'var(--accent)' }} />
        <span className="text-sm tracking-wider font-bold">PROJECT INFO</span>
      </div>

      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-6">
          <div>
            <div className="text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>NAME</div>
            <div className="text-sm">{data.data?.name}</div>
          </div>
          <div>
            <div className="text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>PATH</div>
            <div className="text-sm truncate">{data.data?.path}</div>
          </div>
          <div>
            <div className="text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>DJANGO</div>
            <div className="text-sm" style={{ color: data.data?.is_django ? 'var(--success)' : 'var(--error)' }}>
              {data.data?.is_django ? 'YES' : 'NO'}
            </div>
          </div>
        </div>

        <div>
          <div className="text-xs tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>APPS ({data.data?.apps?.length || 0})</div>
          <div className="border" style={{ borderColor: 'var(--border)' }}>
            {data.data?.apps?.length ? (
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ background: 'var(--bg-tertiary)' }}>
                    <th className="text-left px-3 py-2 text-xs tracking-wider" style={{ color: 'var(--text-muted)' }}>#</th>
                    <th className="text-left px-3 py-2 text-xs tracking-wider" style={{ color: 'var(--text-muted)' }}>APP NAME</th>
                  </tr>
                </thead>
                <tbody>
                  {data.data.apps.map((app, i) => (
                    <tr key={app} style={{ borderTop: '1px solid var(--border)' }}>
                      <td className="px-3 py-2" style={{ color: 'var(--text-muted)' }}>{i + 1}</td>
                      <td className="px-3 py-2">{app}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="px-3 py-4 text-sm" style={{ color: 'var(--text-muted)' }}>No apps found</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
