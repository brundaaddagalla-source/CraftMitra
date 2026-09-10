import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { LanguageProvider } from "./context/LanguageContext";
import { AuthProvider, useAuth } from "./context/AuthContext";
import AppLayout from "./components/AppLayout";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import AddProduct from "./pages/AddProduct";
import VoiceCapture from "./pages/VoiceCapture";
import AIProcessing from "./pages/AIProcessing";
import ProductCatalog from "./pages/ProductCatalog";
import EditProduct from "./pages/EditProduct";
import PublishProduct from "./pages/PublishProduct";
import MyProducts from "./pages/MyProducts";
import OrderHistory from "./pages/OrderHistory";

function RequireAuth({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/signup" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/signup" element={<Signup />} />

      <Route
        path="/*"
        element={
          <RequireAuth>
            <AppLayout>
              <Routes>
                <Route path="/" element={<MyProducts />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/add-product" element={<AddProduct />} />
                <Route path="/voice-capture" element={<VoiceCapture />} />
                <Route path="/ai-processing" element={<AIProcessing />} />
                <Route path="/product-catalog" element={<ProductCatalog />} />
                <Route path="/edit-product" element={<EditProduct />} />
                <Route path="/publish" element={<PublishProduct />} />
                <Route path="/my-products" element={<MyProducts />} />
                <Route path="/orders" element={<OrderHistory />} />
              </Routes>
            </AppLayout>
          </RequireAuth>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;