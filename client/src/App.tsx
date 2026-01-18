import {Routes, Route} from "react-router-dom";
import Header from "./components/Header";
import StockDashboard from "./components/StockDashboard";
import MarketBanner from "./components/MarketBanner";
import StockDetail from "./pages/StockDetail";

function App() {
  return (
    <div className="min-h-screen bg-rh-black text-rh-text font-sans selection:bg-rh-green selection:text-black">

      <Header/>

      <main className="max-w-[1600px] mx-auto px-6 py-8">
        <Routes>
          {/* 메인 페이지 */}
          <Route path="/" element={
            <>
              <MarketBanner/>
              <StockDashboard/>
            </>
          }/>

          {/* 상세 페이지 */}
          <Route path="/stock/:symbol" element={<StockDetail/>}/>
        </Routes>
      </main>
    </div>
  )
}

export default App
