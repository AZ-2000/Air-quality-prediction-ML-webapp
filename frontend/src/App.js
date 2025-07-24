import './App.css';
import Navbar from './components/Navbar';
import LandingPage from './components/Landingpage';
import Predictions from './components/Predictions';
import { Routes, Route } from "react-router-dom";
import WaveBackground from './components/WaveComponent';
import HistoricalData from './components/History';
import { SharedContextProvider } from './components/SharedContext';
function App() {
  return (
    <div>
      <SharedContextProvider>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/predictions" element={<Predictions />} />
        <Route path="/history" element={<HistoricalData />} />
      </Routes>
      </SharedContextProvider>
    </div>
  );
}

export default App;
