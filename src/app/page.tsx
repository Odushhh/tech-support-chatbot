import { ThemeToggle } from './components/theme-toggle'

export default function Home() {
  return (
    <main className="bg-gray-100 dark:bg-gray-900 min-h-screen">
      <ThemeToggle />
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-gray-100 mb-4">Customer Service Chatbot for Tech Support</h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">Hello! 👋 I'm your Tech Support Assistant, here to help with all software-related & programming questions.</p>
          <p className="text-xl text-gray-600 dark:text-gray-300">Whether you're stuck coding or debugging, I'm here to assist. Let's get started! 🚀</p>
        </header>

        <div className="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-base p-6">
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200 mb-4">How can I help you today? I specialise in:</h2>
            <ul>
              <li className="text-base font-medium text-gray-600 dark:text-gray-300">💻 <b>Coding Guidance:</b> Debugging, Coding best practices, learning tips.</li>
              <li className="text-base font-medium text-gray-600 dark:text-gray-300">🔧 <b>Troubleshooting:</b> Resolving software issues, Providing technical advice.</li>
              <li className="text-base font-medium text-gray-600 dark:text-gray-300">📚 <b>Programming Help:</b> Algorithms, tools, frameworks, resources.</li>
              <li className="text-base font-medium text-gray-600 dark:text-gray-300">🌐 <b>Tech Support:</b> Assistance with software tools, systems & development environments.</li>
            </ul>
          </div>
          
          <div className="w-full h-[600px] rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
            <iframe
              src="https://www.chatbase.co/chatbot-iframe/VGQpDsWSnbAgj0x7qwSO5"
              className="w-full border-gray-200 dark:border-gray-700 rounded-lg shadow-base"
              width="100%"
              height="100%"
              frameBorder="0"
            />
          </div>
        </div>

        <footer className="text-center mt-12 text-gray-600 dark:text-gray-400">
          <p>© 2024 IS Project - Customer Service Chatbot for Tech Support made by Adrian Oduma.</p>
        </footer>
      </div>
    </main>
  )
}