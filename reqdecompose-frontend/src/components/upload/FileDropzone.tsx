'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Cloud, File, X, Upload, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface FileDropzoneProps {
  onFileSelect: (file: File | null) => void;
  selectedFile: File | null;
  maxSize?: number; // in MB
  accept?: string[];
  isUploading?: boolean;
  uploadProgress?: number;
  error?: string | null;
}

export function FileDropzone({
  onFileSelect,
  selectedFile,
  maxSize = 20,
  accept = ['.pdf', '.docx', '.txt'],
  isUploading = false,
  uploadProgress = 0,
  error,
}: FileDropzoneProps) {
  const [dragError, setDragError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setDragError(null);

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors[0]?.code === 'file-too-large') {
          setDragError(`File is too large. Maximum size is ${maxSize}MB.`);
        } else if (rejection.errors[0]?.code === 'file-invalid-type') {
          setDragError(`Invalid file type. Accepted: ${accept.join(', ')}`);
        } else {
          setDragError('File validation failed. Please try another file.');
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect, maxSize, accept]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: accept.reduce((acc, ext) => {
      if (ext === '.pdf') acc['application/pdf'] = ['.pdf'];
      if (ext === '.docx')
        acc['application/vnd.openxmlformats-officedocument.wordprocessingml.document'] = [
          '.docx',
        ];
      if (ext === '.txt') acc['text/plain'] = ['.txt'];
      return acc;
    }, {} as Record<string, string[]>),
    maxSize: maxSize * 1024 * 1024,
    maxFiles: 1,
    disabled: isUploading,
  });

  const handleRemove = () => {
    onFileSelect(null);
    setDragError(null);
  };

  const hasError = !!error || !!dragError;
  const displayError = error || dragError;

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={cn(
            'relative border-2 border-dashed rounded-lg p-12 transition-all cursor-pointer',
            'hover:border-accent-blue/50 hover:bg-accent-blue/5',
            isDragActive && !isDragReject && 'border-accent-blue bg-accent-blue/10',
            isDragReject && 'border-accent-red bg-accent-red/5',
            hasError && 'border-accent-red',
            !isDragActive && !hasError && 'border-border-default',
            isUploading && 'opacity-50 cursor-not-allowed'
          )}
        >
          <input {...getInputProps()} />

          <div className="flex flex-col items-center justify-center text-center space-y-4">
            {/* Icon */}
            <div
              className={cn(
                'w-16 h-16 rounded-full flex items-center justify-center transition-colors',
                isDragActive && !isDragReject && 'bg-accent-blue/20',
                isDragReject && 'bg-accent-red/20',
                !isDragActive && 'bg-bg-tertiary'
              )}
            >
              <Cloud
                className={cn(
                  'w-8 h-8 transition-colors',
                  isDragActive && !isDragReject && 'text-accent-blue',
                  isDragReject && 'text-accent-red',
                  !isDragActive && 'text-text-tertiary'
                )}
              />
            </div>

            {/* Text */}
            <div>
              <p className="text-base font-medium text-text-primary mb-1">
                {isDragActive && !isDragReject && 'Drop your file here'}
                {isDragReject && 'Invalid file type or size'}
                {!isDragActive && 'Click to upload or drag and drop'}
              </p>
              <p className="text-sm text-text-secondary">
                {accept.join(', ').toUpperCase()} (MAX. {maxSize}MB)
              </p>
            </div>
          </div>
        </div>
      ) : (
        /* Selected File Preview */
        <div
          className={cn(
            'border-2 rounded-lg p-6 transition-all',
            isUploading && 'border-accent-blue',
            !isUploading && 'border-border-default'
          )}
        >
          <div className="flex items-start gap-4">
            {/* File Icon */}
            <div className="flex-shrink-0">
              <div className="w-12 h-12 rounded-lg bg-accent-blue/10 flex items-center justify-center">
                <File className="w-6 h-6 text-accent-blue" />
              </div>
            </div>

            {/* File Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-4 mb-2">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-text-secondary">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>

                {!isUploading && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleRemove}
                    className="flex-shrink-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>

              {/* Upload Progress */}
              {isUploading && (
                <div className="space-y-2">
                  <Progress value={uploadProgress} className="h-2" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-text-secondary">
                      Uploading... {uploadProgress}%
                    </span>
                    <Upload className="h-3 w-3 text-accent-blue animate-pulse" />
                  </div>
                </div>
              )}

              {/* Success State */}
              {!isUploading && uploadProgress === 100 && (
                <div className="flex items-center gap-2 text-accent-green">
                  <CheckCircle2 className="h-4 w-4" />
                  <span className="text-xs font-medium">Upload complete</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {displayError && (
        <div className="flex items-start gap-2 p-3 rounded-lg bg-accent-red/10 border border-accent-red/20">
          <AlertCircle className="h-4 w-4 text-accent-red flex-shrink-0 mt-0.5" />
          <p className="text-sm text-accent-red">{displayError}</p>
        </div>
      )}
    </div>
  );
}
