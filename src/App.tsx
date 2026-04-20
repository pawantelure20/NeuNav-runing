import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "@/lib/api";

// Pages
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Quiz from "./pages/Quiz";
import Dashboard from "./pages/Dashboard";
import RoadmapView from "./pages/RoadmapView";
import LearningTips from "./pages/LearningTips";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();


// 🔹 Loader Component (Reusable)
const Loader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
  </div>
);


// 🔹 Protected Route
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) return <Loader />;
  if (!user) return <Navigate to="/login" replace />;

  return <>{children}</>;
}


// 🔹 Public Route
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) return <Loader />;
  if (user) return <Navigate to="/dashboard" replace />;

  return <>{children}</>;
}


// 🔹 App Layout Wrapper
const AppLayout = ({ children }: { children: React.ReactNode }) => (
  <div
    className="min-h-screen"
    style={{
      background:
        "linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 25%, #cbd5e1 50%, #b6c7d1 75%, #a3b4c7 100%)",
      fontFamily: "Inter, system-ui, -apple-system, sans-serif",
    }}
  >
    <Toaster />
    {children}
  </div>
);


// 🔹 Main App
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AppLayout>
          <BrowserRouter>
            <Routes>

              {/* 🌐 Public Routes */}
              <Route
                path="/"
                element={
                  <PublicRoute>
                    <Index />
                  </PublicRoute>
                }
              />

              <Route
                path="/login"
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                }
              />

              <Route
                path="/register"
                element={
                  <PublicRoute>
                    <Register />
                  </PublicRoute>
                }
              />


              {/* 🔒 Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/quiz"
                element={
                  <ProtectedRoute>
                    <Quiz />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/roadmap/:id"
                element={
                  <ProtectedRoute>
                    <RoadmapView />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/learning-tips"
                element={
                  <ProtectedRoute>
                    <LearningTips />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />


              {/* ❌ Fallback */}
              <Route path="*" element={<NotFound />} />

            </Routes>
          </BrowserRouter>
        </AppLayout>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;