import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'LAZYDjango - Django Code Generator',
  description: 'Auto-generate Django code via Web UI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
