$ErrorActionPreference='Stop'
$word=$null
$doc=$null
$closeSave=$false
$prepRoot='E:\11-工作\001-workbuddy spaceV1\001-workbuddy space\109-论文写作\01-lunwen\research\sessions\20261102-1917\roles\role5\R003'
$cache=Join-Path $prepRoot 'local-cache'
[string]$template=Join-Path (Split-Path (Split-Path $prepRoot -Parent) -Parent) 'role3\R001\local-cache\建筑结构-正刊排版模板-2024.4.28.doc'
try {
 $word=New-Object -ComObject Word.Application
 $word.Visible=$false
 $word.DisplayAlerts=0
 $word.AutomationSecurity=3
 $confirm=$false
 $readonly=$true
 $doc=$word.Documents.Open([ref]$template,[ref]$confirm,[ref]$readonly)
 $sections=@()
 for($i=1;$i -le $doc.Sections.Count;$i++){
  $section=$doc.Sections.Item($i)
  $page=$section.PageSetup
  $cols=@()
  for($j=1;$j -le $page.TextColumns.Count;$j++){
   $col=$page.TextColumns.Item($j)
   $cols+=@{index=$j;width_pt=$col.Width;space_after_pt=$col.SpaceAfter}
  }
  $sections+=@{index=$i;start=$section.Range.Start;end=$section.Range.End;page_width_pt=$page.PageWidth;page_height_pt=$page.PageHeight;top_pt=$page.TopMargin;bottom_pt=$page.BottomMargin;left_pt=$page.LeftMargin;right_pt=$page.RightMargin;header_distance_pt=$page.HeaderDistance;footer_distance_pt=$page.FooterDistance;section_start=$page.SectionStart;columns=$cols;lines_page=$page.LinesPage;layout_mode=$page.LayoutMode;different_first_header_footer=$page.DifferentFirstPageHeaderFooter}
 }
 $paragraphs=@()
 for($i=1;$i -le $doc.Paragraphs.Count;$i++){
  $p=$doc.Paragraphs.Item($i)
  $text=$p.Range.Text.Trim()
  if($text.Length -gt 160){$text=$text.Substring(0,160)}
  $f=$p.Range.Font
  $pf=$p.Format
  $paragraphs+=@{index=$i;start=$p.Range.Start;end=$p.Range.End;text=$text;style=$p.Style.NameLocal;font=$f.Name;font_east=$f.NameFarEast;size_pt=$f.Size;bold=$f.Bold;italic=$f.Italic;alignment=$pf.Alignment;line_spacing_rule=$pf.LineSpacingRule;line_spacing_pt=$pf.LineSpacing;before_pt=$pf.SpaceBefore;after_pt=$pf.SpaceAfter;first_indent_pt=$pf.FirstLineIndent;left_indent_pt=$pf.LeftIndent}
 }
 $report=@{template=$template;read_only=$doc.ReadOnly;automation_security=$word.AutomationSecurity;word_version=$word.Version;pages=$doc.ComputeStatistics(2);sections=$sections;paragraphs=$paragraphs;table_count=$doc.Tables.Count;inline_shapes=$doc.InlineShapes.Count;floating_shapes=$doc.Shapes.Count;fields=$doc.Fields.Count}
 $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $cache 'template-audit.json') -Encoding UTF8
 $pdf=Join-Path $cache 'template-reference.pdf'
 $doc.ExportAsFixedFormat($pdf,17)
} finally {
 try {
  if($null -ne $doc){try{$doc.Close([ref]$closeSave)}finally{[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc)}}
 } finally {
  if($null -ne $word){try{$word.Quit([ref]$closeSave)}finally{[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)}}
 }
}
