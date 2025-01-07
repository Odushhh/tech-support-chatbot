import { Metadata } from 'next'
import { ThemeProvider } from './components/theme-provider'

export const metadata: Metadata = {
  title: 'Tech Support Chatbot',
  description: 'Customer Service Chatbot for Tech Support',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script src="https://cdn.tailwindcss.com" />
      </head>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}