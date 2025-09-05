// UI components
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
// React Query for data fetching
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// React Router for navigation
import { BrowserRouter, Routes, Route } from "react-router-dom";
// Theme provider
import { ThemeProvider } from "@/components/theme-provider";
// Page components
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import ContractDetails from "./pages/ContractDetails";
import NotFound from "./pages/NotFound";
// Create React Query client
const queryClient = new QueryClient();
// Main App component
const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider defaultTheme="system" storageKey="contract-intelligence-theme">
      <TooltipProvider>
        <Toaster />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contracts" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/contracts/:id" element={<ContractDetails />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
