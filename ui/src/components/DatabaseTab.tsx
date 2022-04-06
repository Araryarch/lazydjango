'use client'

import { useState, useEffect } from 'react'
import { Database, Box, ArrowRight, RefreshCw, Link2 } from 'lucide-react'

interface DatabaseProps {
  apiUrl: string
  projectPath: string
}

interface Field {
  name: string
  type: string
  to?: string
}

interface Relationship {
  name: string
  type: string
  to_model: string
}

interface Model {
  name: string
  fields: Field[]
  relationships: Relationship[]
}

interface AppDetail {
  name: string
  models: Model[]
  routes: { path: string; view: string; model: string }[]
}

interface ProjectData {
  success: boolean
  data?: {
    path: string
    name: string
    apps: string[]
    app_details: AppDetail[]
    is_django: boolean
  }
  detail?: string
}

const fieldTypeColors: Record<string, string> = {
  CharField: 'var(--accent)',
  TextField: 'var(--accent)',
  IntegerField: '#10b981',
  FloatField: '#10b981',
  BooleanField: '#f59e0b',
  DateField: '#8b5cf6',
  DateTimeField: '#8b5cf6',
  ForeignKey: '#ef4444',
  ManyToManyField: '#ec4899',
  OneToOneField: '#f97316',
  EmailField: '#06b6d4',
  URLField: '#06b6d4',
  ImageField: '#84cc16',
  FileField: '#84cc16',
  JSONField: '#a855f7',
  UUIDField: '#6366f1',
  SlugField: '#14b8a6',
}

export default function DatabaseTab({ apiUrl, projectPath }: DatabaseProps) {
  const [data, setData] = useState<ProjectData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedApp, setSelectedApp] = useState<string | null>(null)
  const [selectedModel, setSelectedModel] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'tables' | 'erd'>('tables')

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${apiUrl}/api/project/?project_path=${encodeURIComponent(projectPath)}`)
      const json = await res.json()
      setData(json)
      if (json.success && json.data?.app_details?.length) {
        setSelectedApp(json.data.app_details[0].name)
      }
    } catch (e) {
      setError('Failed to connect to API')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [apiUrl, projectPath])

  const allModels = data?.data?.app_details?.flatMap(app => 
    app.models.map(m => ({ ...m, appName: app.name }))
  ) || []

  const selectedAppData = data?.data?.app_details?.find(a => a.name === selectedApp)
  const selectedModelData = selectedAppData?.models?.find(m => m.name === selectedModel)
  
  const relationships = allModels.flatMap(m => 
    m.relationships.map(r => ({
      ...r,
      fromModel: m.name,
      fromApp: m.appName
    }))
  )

  const getFieldIcon = (type: string) => {
    if (type === 'ForeignKey' || type === 'ManyToManyField' || type === 'OneToOneField') {
      return <Link2 className="w-3 h-3" style={{ color: fieldTypeColors[type] }} />
    }
    return <Box className="w-3 h-3" style={{ color: fieldTypeColors[type] || 'var(--text-muted)' }} />
  }

  const getRelationSymbol = (type: string) => {
    switch (type) {
      case 'ManyToOne': return '───►'
      case 'OneToOne': return '──═►'
      case 'ManyToMany': return '◄───►'
      default: return '───►'
    }
  }

  if (loading) {
    return <div style={{ color: 'var(--text-secondary)' }}>Loading...</div>
  }

  if (error || !data?.success) {
    return (
      <div>
        <div className="flex items-center justify-between pb-4 mb-4" style={{ borderBottom: '1px solid var(--border)' }}>
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5" style={{ color: 'var(--accent)' }} />
            <span className="text-sm tracking-wider font-bold">DATABASE</span>
          </div>
          <button onClick={fetchData} className="flex items-center gap-1 text-xs px-2 py-1" style={{ color: 'var(--text-muted)' }}>
            <RefreshCw className="w-3 h-3" /> RETRY
          </button>
        </div>
        <div style={{ color: 'var(--error)' }} className="text-sm">{error || data?.detail || 'Not a Django project'}</div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5" style={{ color: 'var(--accent)' }} />
          <span className="text-sm tracking-wider font-bold">DATABASE</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex" style={{ background: 'var(--bg-tertiary)', borderRadius: '4px' }}>
            <button
              onClick={() => setViewMode('tables')}
              className="px-3 py-1 text-xs"
              style={{
                background: viewMode === 'tables' ? 'var(--accent)' : 'transparent',
                color: viewMode === 'tables' ? 'var(--bg)' : 'var(--text-secondary)',
                borderRadius: '4px'
              }}
            >
              TABLES
            </button>
            <button
              onClick={() => setViewMode('erd')}
              className="px-3 py-1 text-xs"
              style={{
                background: viewMode === 'erd' ? 'var(--accent)' : 'transparent',
                color: viewMode === 'erd' ? 'var(--bg)' : 'var(--text-secondary)',
                borderRadius: '4px'
              }}
            >
              ERD
            </button>
          </div>
          <button onClick={fetchData} className="p-2" title="Refresh">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {viewMode === 'tables' ? (
          <>
            {/* Apps & Models List */}
            <div className="w-56 border-r overflow-y-auto" style={{ borderColor: 'var(--border)' }}>
              <div className="p-2">
                <div className="text-xs tracking-wider mb-2 px-2" style={{ color: 'var(--text-muted)' }}>APPS</div>
                {data.data?.app_details?.map(app => (
                  <div key={app.name} className="mb-2">
                    <button
                      onClick={() => { setSelectedApp(app.name); setSelectedModel(null) }}
                      className="w-full text-left px-2 py-1.5 text-xs rounded"
                      style={{
                        background: selectedApp === app.name ? 'var(--accent)' : 'transparent',
                        color: selectedApp === app.name ? 'var(--bg)' : 'var(--text)',
                      }}
                    >
                      {app.name}
                    </button>
                    {selectedApp === app.name && (
                      <div className="ml-2 mt-1">
                        {app.models.map(model => (
                          <button
                            key={model.name}
                            onClick={() => setSelectedModel(model.name)}
                            className="w-full text-left px-2 py-1 text-xs rounded flex items-center gap-1"
                            style={{
                              background: selectedModel === model.name ? 'var(--bg-tertiary)' : 'transparent',
                              color: selectedModel === model.name ? 'var(--accent)' : 'var(--text-secondary)',
                            }}
                          >
                            <Box className="w-3 h-3" />
                            {model.name}
                          </button>
                        ))}
                        {app.models.length === 0 && (
                          <div className="text-xs px-2 py-1" style={{ color: 'var(--text-muted)' }}>No models</div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Model Details */}
            <div className="flex-1 p-4 overflow-y-auto">
              {selectedModel && selectedModelData ? (
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <Box className="w-5 h-5" style={{ color: 'var(--accent)' }} />
                    <h2 className="text-lg font-bold">{selectedModelData.name}</h2>
                    <span className="text-xs px-2 py-0.5 rounded" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-muted)' }}>
                      {selectedApp}
                    </span>
                  </div>

                  {/* Fields */}
                  <div className="mb-6">
                    <h3 className="text-xs tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>FIELDS</h3>
                    <div className="border rounded" style={{ borderColor: 'var(--border)' }}>
                      <table className="w-full text-sm">
                        <thead>
                          <tr style={{ background: 'var(--bg-tertiary)' }}>
                            <th className="text-left px-3 py-2 text-xs" style={{ color: 'var(--text-muted)' }}>NAME</th>
                            <th className="text-left px-3 py-2 text-xs" style={{ color: 'var(--text-muted)' }}>TYPE</th>
                            <th className="text-left px-3 py-2 text-xs" style={{ color: 'var(--text-muted)' }}>TO</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedModelData.fields.map((field, i) => (
                            <tr key={i} style={{ borderTop: '1px solid var(--border)' }}>
                              <td className="px-3 py-2 flex items-center gap-2">
                                {getFieldIcon(field.type)}
                                <span className="font-mono">{field.name}</span>
                              </td>
                              <td className="px-3 py-2">
                                <span className="px-2 py-0.5 rounded text-xs" style={{ 
                                  background: fieldTypeColors[field.type] + '20',
                                  color: fieldTypeColors[field.type] || 'var(--text)'
                                }}>
                                  {field.type}
                                </span>
                              </td>
                              <td className="px-3 py-2" style={{ color: field.to ? 'var(--accent)' : 'var(--text-muted)' }}>
                                {field.to || '-'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Relationships */}
                  {selectedModelData.relationships.length > 0 && (
                    <div>
                      <h3 className="text-xs tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>RELATIONSHIPS</h3>
                      <div className="border rounded p-3" style={{ borderColor: 'var(--border)' }}>
                        {selectedModelData.relationships.map((rel, i) => (
                          <div key={i} className="flex items-center gap-2 text-sm mb-2 last:mb-0">
                            <span style={{ color: 'var(--text-muted)' }}>{getRelationSymbol(rel.type)}</span>
                            <span className="font-mono">{rel.name}</span>
                            <span style={{ color: 'var(--text-muted)' }}>({rel.type})</span>
                            <ArrowRight className="w-3 h-3" style={{ color: 'var(--text-muted)' }} />
                            <span style={{ color: 'var(--accent)' }}>{rel.to_model}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full" style={{ color: 'var(--text-muted)' }}>
                  Select a model to view details
                </div>
              )}
            </div>
          </>
        ) : (
          /* ERD View */
          <div className="flex-1 p-4 overflow-auto">
            <div className="mb-4">
              <h3 className="text-xs tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>ENTITY RELATIONSHIP DIAGRAM</h3>
            </div>
            
            {allModels.length === 0 ? (
              <div className="flex items-center justify-center h-64" style={{ color: 'var(--text-muted)' }}>
                No models to display
              </div>
            ) : (
              <div className="flex flex-wrap gap-6">
                {allModels.map(model => (
                  <div
                    key={`${model.appName}-${model.name}`}
                    className="border rounded-lg overflow-hidden min-w-[240px]"
                    style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
                  >
                    <div className="px-3 py-2 flex items-center gap-2" style={{ background: 'var(--accent)' }}>
                      <Box className="w-4 h-4" style={{ color: 'var(--bg)' }} />
                      <span className="font-bold text-sm" style={{ color: 'var(--bg)' }}>{model.name}</span>
                    </div>
                    <div className="p-2">
                      {model.fields.map((field, i) => (
                        <div key={i} className="flex items-center justify-between py-1 text-xs">
                          <span className="font-mono">{field.name}</span>
                          <span style={{ 
                            color: fieldTypeColors[field.type] || 'var(--text-muted)',
                            fontSize: '10px'
                          }}>
                            {field.type.replace('Field', '')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Relationship Lines */}
            {relationships.length > 0 && (
              <div className="mt-6">
                <h3 className="text-xs tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>RELATIONSHIPS</h3>
                <div className="p-4 border rounded" style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}>
                  <table className="w-full text-sm">
                    <thead>
                      <tr style={{ background: 'var(--bg-tertiary)' }}>
                        <th className="text-left px-3 py-2 text-xs" style={{ color: 'var(--text-muted)' }}>FROM</th>
                        <th className="text-left px-3 py-2 text-xs" style={{ color: 'var(--text-muted)' }}>TYPE</th>
                        <th className="text-left px-3 py-2 text-xs" style={{ color: 'var(--text-muted)' }}>TO</th>
                      </tr>
                    </thead>
                    <tbody>
                      {relationships.map((rel, i) => (
                        <tr key={i} style={{ borderTop: '1px solid var(--border)' }}>
                          <td className="px-3 py-2">
                            <span className="font-mono">{rel.fromModel}</span>
                            <span className="text-xs ml-1" style={{ color: 'var(--text-muted)' }}>({rel.fromApp})</span>
                          </td>
                          <td className="px-3 py-2">
                            <span className="px-2 py-0.5 rounded text-xs" style={{ background: 'var(--accent)20', color: 'var(--accent)' }}>
                              {rel.type}
                            </span>
                          </td>
                          <td className="px-3 py-2 font-mono" style={{ color: 'var(--accent)' }}>
                            {rel.to_model}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
