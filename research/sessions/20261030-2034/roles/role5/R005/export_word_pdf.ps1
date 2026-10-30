param([string]$TaskDocPath,[string]$TaskPdfPath)
$ErrorActionPreference='Stop'
$TaskWord=$null
$TaskDocument=$null
$TaskSaveNone=0
$TaskFalse=$false
$TaskTrue=$true
try {
 $TaskWord=New-Object -ComObject Word.Application
 $TaskWord.Visible=$false
 $TaskWord.DisplayAlerts=0
 $TaskDocument=$TaskWord.Documents.Open([ref]$TaskDocPath,[ref]$TaskFalse,[ref]$TaskTrue,[ref]$TaskFalse)
 $TaskDocument.Repaginate()
 $TaskDocument.ExportAsFixedFormat($TaskPdfPath,17)
 $TaskDocument.Close([ref]$TaskSaveNone)
 $TaskDocument=$null
 $TaskWord.Quit([ref]$TaskSaveNone)
 $TaskWord=$null
 Write-Output 'WORD_PDF_EXPORT_OK'
} finally {
 if ($null -ne $TaskDocument) {try {$TaskDocument.Close([ref]$TaskSaveNone)} catch {}}
 if ($null -ne $TaskWord) {try {$TaskWord.Quit([ref]$TaskSaveNone)} catch {}}
}
