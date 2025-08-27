import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { FileX, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <Card className="card-elegant max-w-md w-full">
        <CardHeader className="text-center">
          <FileX className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <CardTitle className="text-2xl font-bold">Page Not Found</CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <p className="text-muted-foreground">
            The page you're looking for doesn't exist or has been moved.
          </p>
          <div className="space-y-2">
            <Button asChild className="w-full">
              <a href="/contracts">
                <Home className="h-4 w-4 mr-2" />
                Go to Dashboard
              </a>
            </Button>
            <Button asChild variant="outline" className="w-full">
              <a href="/upload">
                Upload Contract
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NotFound;
