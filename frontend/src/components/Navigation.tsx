import { FileText, Upload, BarChart3 } from "lucide-react";
import { NavLink } from "react-router-dom";
import { Button } from "@/components/ui/button";

const Navigation = () => {
  const navItems = [
    { to: "/contracts", label: "Contracts", icon: FileText },
    { to: "/upload", label: "Upload", icon: Upload },
  ];

  return (
    <header className="border-b border-border bg-card">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-8 w-8 text-primary" />
            <h1 className="text-xl font-bold gradient-text">
              Contract Intelligence
            </h1>
          </div>
          
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
        
        <div className="flex items-center space-x-4">
          <Button asChild size="sm">
            <NavLink to="/upload">
              <Upload className="h-4 w-4 mr-2" />
              Upload Contract
            </NavLink>
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Navigation;