import {useState} from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-rh-black text-rh-text p-4">

      {/* 로고 영역 */}
      <div className="text-center mb-10">
        <h1 className="text-6xl font-black tracking-tighter mb-4">
          TICK<span className="text-rh-green">ER</span>
        </h1>
        <p className="text-rh-subtext text-xl font-medium">
          React & TypeScript & tailwindcss
        </p>
      </div>

      {/* 카드 영역 */}
      <div
        className="w-full max-w-md bg-rh-dark border border-rh-gray rounded-2xl p-8 shadow-2xl transition-all hover:border-rh-green hover:-translate-y-1">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold">Robinhood Markets Inc</h2>
            <p className="text-rh-subtext">HOOD</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">$108.74</p>
            <div
              className="flex items-center justify-end text-rh-red font-bold text-sm bg-rh-red/10 px-2 py-1 rounded">
              <span>▼ 1.45%</span>
            </div>
          </div>
        </div>

        <button
          onClick={() => setCount((c) => c + 1)}
          className="w-full bg-rh-green text-black font-bold py-4 rounded-xl hover:opacity-90 active:scale-95 transition-all cursor-pointer text-lg"
        >
          Count ({count})
        </button>
      </div>

    </div>
  )
}

export default App
