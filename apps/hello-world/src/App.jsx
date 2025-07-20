import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [message, setMessage] = useState('')

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const greetings = [
    'Hello World!',
    'שלום עולם!',
    'Hola Mundo!',
    'Bonjour le Monde!',
    'Hallo Welt!',
    'Ciao Mondo!',
    'こんにちは世界！',
    '你好世界！'
  ]

  const getRandomGreeting = () => {
    const randomIndex = Math.floor(Math.random() * greetings.length)
    setMessage(greetings[randomIndex])
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="logos">
          <a href="https://vite.dev" target="_blank" rel="noopener noreferrer">
            <img src={viteLogo} className="logo" alt="Vite logo" />
          </a>
          <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
            <img src={reactLogo} className="logo react" alt="React logo" />
          </a>
        </div>
        
        <h1>Hello World React App</h1>
        
        <div className="info-section">
          <p className="description">
            This is a standalone React app served through the Hugo blog! 🚀
          </p>
          
          <div className="time-display">
            <p>Current time: <strong>{currentTime.toLocaleString()}</strong></p>
          </div>
        </div>

        <div className="interaction-section">
          <div className="counter-card">
            <button onClick={() => setCount((count) => count + 1)} className="counter-button">
              You clicked {count} times
            </button>
          </div>
          
          <div className="greeting-card">
            <button onClick={getRandomGreeting} className="greeting-button">
              Get Random Greeting
            </button>
            {message && (
              <div className="greeting-message">
                <h2>{message}</h2>
              </div>
            )}
          </div>
        </div>

        <div className="features-section">
          <h3>This app demonstrates:</h3>
          <ul>
            <li>✅ React with Vite</li>
            <li>✅ State management with hooks</li>
            <li>✅ Real-time clock</li>
            <li>✅ Interactive components</li>
            <li>✅ Integration with Hugo blog</li>
            <li>✅ CI/CD deployment</li>
          </ul>
        </div>

        <div className="navigation">
          <a href="/" className="back-link">← Back to Blog</a>
          <a href="/posts" className="posts-link">View Posts →</a>
        </div>
      </header>
    </div>
  )
}

export default App
