import { BrowserRouter, Routes, Route } from "react-router-dom";

import { LanguageProvider } from "./context/LanguageContext";
import AppLayout from "./components/AppLayout";
import Dashboard from "./pages/Dashboard";
import AddProduct from "./pages/AddProduct";
import AIProcessing from "./pages/AIProcessing";
import ProductCatalog from "./pages/ProductCatalog";
import EditProduct from "./pages/EditProduct";
import PublishProduct from "./pages/PublishProduct";
import MyProducts from "./pages/MyProducts";
import OrderHistory from "./pages/OrderHistory";

function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <AppLayout>
          <Routes>
          <Route path="/" element={<MyProducts />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/add-product" element={<AddProduct />} />
          <Route path="/ai-processing" element={<AIProcessing />} />
          <Route path="/product-catalog" element={<ProductCatalog />} />
          <Route path="/edit-product" element={<EditProduct />} />
          <Route path="/publish" element={<PublishProduct />} />
          <Route path="/my-products" element={<MyProducts />} />
          <Route path="/orders" element={<OrderHistory />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;
