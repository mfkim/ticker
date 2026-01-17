import Header from "./components/Header";
import StockDashboard from "./components/StockDashboard";
import MarketBanner from "./components/MarketBanner.tsx";

function App() {
  return (
    <div className="min-h-screen bg-rh-black text-rh-text font-sans selection:bg-rh-green selection:text-black">

      <Header/>

      <main className="max-w-[1600px] mx-auto px-6 py-8">
        <MarketBanner />
        <StockDashboard/>
      </main>
    </div>
  )
}

export default App
