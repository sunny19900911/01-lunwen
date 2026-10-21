param([Parameter(Mandatory=$true)][string]$DocxPath,[Parameter(Mandatory=$true)][string]$PdfPath)
$ErrorActionPreference = 'Stop'
$inputDocx = [System.IO.Path]::GetFullPath($DocxPath)
$outputPdf = [System.IO.Path]::GetFullPath($PdfPath)
if (-not (Test-Path -LiteralPath $inputDocx)) { throw 'Input missing' }
if (Test-Path -LiteralPath $outputPdf) { throw 'Refuse to overwrite render' }
$wordApp = $null
$wordDoc = $null
try {
  $wordApp = New-Object -ComObject Word.Application
  $wordApp.Visible = $false
  $wordApp.DisplayAlerts = 0
  $wordApp.AutomationSecurity = 3
  $wordApp.Options.UpdateLinksAtOpen = $false
  $wordApp.Options.SaveNormalPrompt = $false
  $wordDoc = $wordApp.Documents.Open($inputDocx, $false, $true, $false)
  $wordDoc.Repaginate()
  $pages = $wordDoc.ComputeStatistics(2)
  $equations = $wordDoc.OMaths.Count
  $wordDoc.ExportAsFixedFormat($outputPdf, 17)
  @{pages=$pages;equations=$equations;pdf=$outputPdf;renderer='Microsoft Word native hidden instance';source_saved=$false} | ConvertTo-Json -Compress
} finally {
  if ($null -ne $wordDoc) { $wordDoc.Close(0); [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordDoc) | Out-Null }
  if ($null -ne $wordApp) { $wordApp.Quit(0); [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordApp) | Out-Null }
  [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
