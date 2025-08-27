import { useState, useCallback } from "react";
import { Upload as UploadIcon, FileText, X, CheckCircle, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useUploadContract } from "@/services/queries";

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  contractId?: string;
  error?: string;
}

const Upload = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const navigate = useNavigate();
  const uploadMutation = useUploadContract();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const validateFile = (file: File): string | null => {
    // Validate file type
    if (file.type !== 'application/pdf') {
      return "Only PDF files are supported.";
    }

    // Validate file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
      return "File size must be less than 50MB.";
    }

    return null;
  };

  const handleFiles = (files: File[]) => {
    files.forEach(file => {
      const validationError = validateFile(file);
      
      const fileId = Math.random().toString(36).substr(2, 9);
      const uploadFile: UploadedFile = {
        file,
        id: fileId,
        progress: 0,
        status: validationError ? 'error' : 'uploading',
        error: validationError || undefined
      };

      setUploadedFiles(prev => [...prev, uploadFile]);

      if (!validationError) {
        // Start actual upload
        uploadContract(file, fileId);
      }
    });
  };

  const uploadContract = async (file: File, fileId: string) => {
    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadedFiles(prev => 
          prev.map(f => {
            if (f.id === fileId && f.progress < 90) {
              return { ...f, progress: f.progress + Math.random() * 20 };
            }
            return f;
          })
        );
      }, 200);

      const result = await uploadMutation.mutateAsync(file);

      clearInterval(progressInterval);

      setUploadedFiles(prev => 
        prev.map(f => {
          if (f.id === fileId) {
            return {
              ...f,
              progress: 100,
              status: 'completed' as const,
              contractId: result.contract_id
            };
          }
          return f;
        })
      );

      // Auto-redirect after 2 seconds
      setTimeout(() => {
        navigate(`/contracts/${result.contract_id}`);
      }, 2000);

    } catch (error) {
      setUploadedFiles(prev => 
        prev.map(f => {
          if (f.id === fileId) {
            return {
              ...f,
              status: 'error' as const,
              error: error instanceof Error ? error.message : 'Upload failed'
            };
          }
          return f;
        })
      );
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Upload Contract</h1>
            <p className="text-muted-foreground">
              Upload PDF contracts for automated intelligence processing and analysis
            </p>
          </div>

          {/* Upload Zone */}
          <Card className="card-elegant mb-8">
            <CardContent className="p-8">
              <div
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                  dragActive
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-muted/50"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <UploadIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">
                  Drop your PDF contracts here
                </h3>
                <p className="text-muted-foreground mb-4">
                  or click to browse and select files
                </p>
                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={handleFileInput}
                  className="hidden"
                  id="file-upload"
                />
                <Button asChild>
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <UploadIcon className="h-4 w-4 mr-2" />
                    Select PDF Files
                  </label>
                </Button>
                <p className="text-xs text-muted-foreground mt-4">
                  Maximum file size: 50MB • Supported format: PDF only
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Upload Progress */}
          {uploadedFiles.length > 0 && (
            <Card className="card-elegant">
              <CardHeader>
                <CardTitle>Upload Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {uploadedFiles.map((file) => (
                    <div key={file.id} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-8 w-8 text-muted-foreground" />
                          <div>
                            <p className="font-medium">{file.file.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {formatFileSize(file.file.size)}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          {file.status === 'completed' && (
                            <CheckCircle className="h-5 w-5 text-success" />
                          )}
                          {file.status === 'error' && (
                            <AlertCircle className="h-5 w-5 text-destructive" />
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(file.id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      
                      {file.status === 'uploading' && (
                        <div className="mt-2">
                          <Progress value={file.progress} className="w-full" />
                          <p className="text-xs text-muted-foreground mt-1">
                            Uploading... {Math.round(file.progress)}%
                          </p>
                        </div>
                      )}
                      
                      {file.status === 'completed' && (
                        <div className="mt-2">
                          <p className="text-sm text-success">
                            Upload completed! Contract ID: {file.contractId}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Redirecting to contract details...
                          </p>
                        </div>
                      )}
                      
                      {file.status === 'error' && (
                        <div className="mt-2">
                          <p className="text-sm text-destructive">
                            {file.error || 'Upload failed'}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upload Tips */}
          <Card className="card-elegant mt-8">
            <CardHeader>
              <CardTitle>Upload Tips</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-2">Supported Files</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• PDF documents only</li>
                    <li>• Maximum size: 50MB per file</li>
                    <li>• Text-based PDFs work best</li>
                    <li>• Multiple files can be uploaded</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Processing Time</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Small contracts: ~30 seconds</li>
                    <li>• Large contracts: ~2-5 minutes</li>
                    <li>• Processing happens in background</li>
                    <li>• You'll be notified when complete</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Upload;
