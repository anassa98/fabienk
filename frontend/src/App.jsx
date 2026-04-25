import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import MainDashboard from "./pages/MainDashboard";
import ProductivityPage from "./pages/ProductivityPage";
import SocialPage from "./pages/SocialPage";
import EnvironmentalPage from "./pages/EnvironmentalPage";
import EconomicPage from "./pages/EconomicPage";
import FinancialPage from "./pages/FinancialPage";
import { useCities } from "./hooks/useCityData";

export default function App() {
  const [cityCode, setCityCode] = useState(
    () => localStorage.getItem("upa.cityCode") || ""
  );
  const { data: cities } = useCities();

  useEffect(() => {
    if (cityCode) {
      localStorage.setItem("upa.cityCode", cityCode);
    }
  }, [cityCode]);

  useEffect(() => {
    const list = cities?.results ?? cities ?? [];
    if (!cityCode && list.length > 0) {
      setCityCode(list[0].city_code);
    }
  }, [cities, cityCode]);

  const props = { cityCode, setCityCode };

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-5">
        <Routes>
          <Route path="/" element={<MainDashboard {...props} />} />
          <Route path="/productivity" element={<ProductivityPage {...props} />} />
          <Route path="/social" element={<SocialPage {...props} />} />
          <Route path="/environmental" element={<EnvironmentalPage {...props} />} />
          <Route path="/economic" element={<EconomicPage {...props} />} />
          <Route path="/financial" element={<FinancialPage {...props} />} />
        </Routes>
      </main>
    </div>
  );
}
