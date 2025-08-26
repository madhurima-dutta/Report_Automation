"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { Ship, FileSpreadsheet, FolderOpen, CheckCircle, AlertCircle, Loader2 } from "lucide-react"

interface ProcessingResult {
  vessel: string
  owner: string
  status: "success" | "error" | "processing"
  message?: string
}

export default function VesselProcessingApp() {
  const [vesselInput, setVesselInput] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<ProcessingResult[]>([])
  const [error, setError] = useState("")
  const [selectedFormats, setSelectedFormats] = useState<string[]>([])

  const exportOptions = [
    { id: "reporting", label: "Reporting Page" },
    { id: "eua", label: "EUA" },
    { id: "fuel-eu", label: "Fuel EU" },
    { id: "backup", label: "Backup (saved as Excel)" },
    { id: "all", label: "All (Reporting Page + EUA + Fuel EU + Backup)" },
  ]

  const handleFormatChange = (formatId: string, checked: boolean) => {
    if (checked) {
      setSelectedFormats((prev) => [...prev, formatId])
    } else {
      setSelectedFormats((prev) => prev.filter((id) => id !== formatId))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!vesselInput.trim()) {
      setError("Please enter at least one vessel name")
      return
    }

    if (selectedFormats.length === 0) {
      setError("Please select at least one export format")
      return
    }

    setIsProcessing(true)
    setError("")
    setProgress(0)

    // Parse comma-separated vessel names
    const vessels = vesselInput
      .split(",")
      .map((v) => v.trim())
      .filter((v) => v)
    const totalVessels = vessels.length

    // Initialize results
    const initialResults: ProcessingResult[] = vessels.map((vessel) => ({
      vessel,
      owner: "",
      status: "processing",
    }))
    setResults(initialResults)

    // Simulate processing each vessel
    for (let i = 0; i < vessels.length; i++) {
      const vessel = vessels[i]

      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // Mock owner lookup (in real implementation, this would call your Python script)
      const mockOwners = [
        "Schoeller - AAL",
        "Schoeller - Hanse",
        "Frontline Management",
        "Maersk Line",
        "MSC Mediterranean",
      ]
      const owner = mockOwners[Math.floor(Math.random() * mockOwners.length)]

      // Update progress
      const newProgress = ((i + 1) / totalVessels) * 100
      setProgress(newProgress)

      // Update results
      setResults((prev) =>
        prev.map((result, index) =>
          index === i
            ? { ...result, owner, status: "success" as const, message: "Files organized successfully" }
            : result,
        ),
      )
    }

    setIsProcessing(false)
  }

  const getStatusIcon = (status: ProcessingResult["status"]) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "error":
        return <AlertCircle className="h-4 w-4 text-destructive" />
      case "processing":
        return <Loader2 className="h-4 w-4 animate-spin text-secondary" />
    }
  }

  const getStatusBadge = (status: ProcessingResult["status"]) => {
    switch (status) {
      case "success":
        return (
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            Success
          </Badge>
        )
      case "error":
        return <Badge variant="destructive">Error</Badge>
      case "processing":
        return (
          <Badge variant="outline" className="border-secondary text-secondary">
            Processing
          </Badge>
        )
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Ship className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">Vessel Data Processor</h1>
          </div>
          <p className="text-muted-foreground text-lg">
            Organize vessel emission data by owner with automated folder structure
          </p>
        </div>

        {/* Main Processing Card */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5 text-primary" />
              Process Vessel Data
            </CardTitle>
            <CardDescription>Enter vessel names separated by commas and select export formats</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="vessels">Vessel Names</Label>
                <Textarea
                  id="vessels"
                  placeholder="Enter vessel names separated by commas (e.g., FRONT CHEETAH, AAL BRISBANE, AAL DALIAN)"
                  value={vesselInput}
                  onChange={(e) => setVesselInput(e.target.value)}
                  className="min-h-[100px] resize-none"
                  disabled={isProcessing}
                />
                <p className="text-sm text-muted-foreground">Separate multiple vessel names with commas</p>
              </div>

              <div className="space-y-3">
                <Label>Select Export Formats</Label>
                <div className="grid grid-cols-1 gap-3">
                  {exportOptions.map((option) => (
                    <div key={option.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={option.id}
                        checked={selectedFormats.includes(option.id)}
                        onCheckedChange={(checked) => handleFormatChange(option.id, checked as boolean)}
                        disabled={isProcessing}
                      />
                      <Label htmlFor={option.id} className="text-sm font-normal cursor-pointer">
                        {option.label}
                      </Label>
                    </div>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground">Select one or more export formats</p>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button type="submit" className="w-full" disabled={isProcessing} size="lg">
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing Vessels...
                  </>
                ) : (
                  <>
                    <FolderOpen className="mr-2 h-4 w-4" />
                    Process Vessels
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Progress Section */}
        {isProcessing && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-lg">Processing Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Overall Progress</span>
                  <span>{Math.round(progress)}%</span>
                </div>
                <Progress value={progress} className="w-full" />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Section */}
        {results.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-primary" />
                Processing Results
              </CardTitle>
              <CardDescription>Status of vessel data organization by owner</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(result.status)}
                        <div>
                          <h4 className="font-medium text-card-foreground">{result.vessel}</h4>
                          {result.owner && <p className="text-sm text-muted-foreground">Owner: {result.owner}</p>}
                          {result.message && <p className="text-sm text-muted-foreground">{result.message}</p>}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">{getStatusBadge(result.status)}</div>
                    </div>
                    {index < results.length - 1 && <Separator className="my-2" />}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Info Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="text-lg">How It Works</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-start gap-3">
                <div className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                  1
                </div>
                <div>
                  <h4 className="font-medium mb-1">Input Vessels</h4>
                  <p className="text-muted-foreground">Enter vessel names separated by commas</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                  2
                </div>
                <div>
                  <h4 className="font-medium mb-1">Owner Lookup</h4>
                  <p className="text-muted-foreground">System matches vessels to owners using Excel data</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                  3
                </div>
                <div>
                  <h4 className="font-medium mb-1">File Organization</h4>
                  <p className="text-muted-foreground">Creates owner-based folders and organizes files</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
