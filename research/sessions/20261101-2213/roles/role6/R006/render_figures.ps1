param([string]$Suffix = "v001")
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms.DataVisualization
Add-Type -AssemblyName System.Drawing
$data = Get-Content -LiteralPath (Join-Path $PSScriptRoot "plot-data.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$blue = [Drawing.ColorTranslator]::FromHtml("#24779B")
$orange = [Drawing.ColorTranslator]::FromHtml("#C76536")
$ink = [Drawing.ColorTranslator]::FromHtml("#263B48")
$grid = [Drawing.ColorTranslator]::FromHtml("#E1E7EB")
function Font([single]$size,[bool]$bold=$false) {
    $style = if ($bold) {[Drawing.FontStyle]::Bold} else {[Drawing.FontStyle]::Regular}
    return New-Object Drawing.Font("Microsoft YaHei",$size,$style)
}
function Chart([int]$height) {
    $c = New-Object Windows.Forms.DataVisualization.Charting.Chart
    $c.Width=2400; $c.Height=$height; $c.BackColor=[Drawing.Color]::White
    $c.AntiAliasing="All"; $c.TextAntiAliasingQuality="High"
    return ,$c
}
function Title($c,[string]$text,[single]$size,[single]$x,[single]$y,[single]$w,[single]$h,[bool]$bold=$false) {
    $t = New-Object Windows.Forms.DataVisualization.Charting.Title
    $t.Text=$text; $t.Font=Font $size $bold; $t.ForeColor=$ink
    $t.Position=New-Object Windows.Forms.DataVisualization.Charting.ElementPosition($x,$y,$w,$h)
    $t.Alignment="MiddleCenter"
    [void]$c.Titles.Add($t)
}
function Area($c,[string]$name,[single]$x,[single]$y,[single]$w,[single]$h) {
    $a=New-Object Windows.Forms.DataVisualization.Charting.ChartArea($name)
    $a.Position=New-Object Windows.Forms.DataVisualization.Charting.ElementPosition($x,$y,$w,$h)
    $a.BackColor=[Drawing.Color]::White
    foreach($axis in @($a.AxisX,$a.AxisY)) {
        $axis.LabelStyle.Font=Font 21; $axis.LabelStyle.ForeColor=$ink
        $axis.TitleFont=Font 24; $axis.TitleForeColor=$ink
        $axis.LineColor=[Drawing.Color]::FromArgb(110,125,135)
        $axis.MajorTickMark.LineColor=$axis.LineColor
        $axis.MajorGrid.LineColor=$grid; $axis.MajorGrid.LineWidth=1
        $axis.IsLabelAutoFit=$false; $axis.IsStartedFromZero=$false
    }
    [void]$c.ChartAreas.Add($a)
    return ,$a
}
function Export($c,[string]$stem) {
    $png=Join-Path $PSScriptRoot ($stem+"-"+$Suffix+".png")
    $emf=Join-Path $PSScriptRoot ($stem+"-"+$Suffix+".emf")
    if ((Test-Path -LiteralPath $png) -or (Test-Path -LiteralPath $emf)) {throw "Refusing overwrite: $stem $Suffix"}
    $stream=New-Object IO.MemoryStream
    $c.SaveImage($stream,[Windows.Forms.DataVisualization.Charting.ChartImageFormat]::Png)
    $stream.Position=0
    $bitmap=[Drawing.Bitmap]::FromStream($stream)
    $bitmap.SetResolution(300,300)
    $bitmap.Save($png,[Drawing.Imaging.ImageFormat]::Png)
    $bitmap.Dispose(); $stream.Dispose()
    $c.SaveImage($emf,[Windows.Forms.DataVisualization.Charting.ChartImageFormat]::Emf)
    Write-Output $png
    $c.Dispose()
}

# Figure 1: actual floor order on vertical axis, not sensitivity rank.
$c=Chart 1800
Title $c "基准阻尼5%时的楼层剪力改善速度" 32 0 1 100 5 $true
Title $c "SHW3X · 固定300阶线性参照" 22 0 7 100 4
$a=Area $c "profile" 2 13 96 76
$a.InnerPlotPosition=New-Object Windows.Forms.DataVisualization.Charting.ElementPosition(14,3,82,86)
$a.AxisX.Minimum=0; $a.AxisX.Maximum=13; $a.AxisX.Interval=2
$a.AxisX.Title="S（降幅%/阻尼百分点）"
$a.AxisY.Minimum=0.5; $a.AxisY.Maximum=12.5; $a.AxisY.Interval=1
$a.AxisY.Title="楼层"; $a.AxisY.LabelStyle.Format="0"
$a.AxisY.MajorGrid.Enabled=$false
$line=New-Object Windows.Forms.DataVisualization.Charting.Series("S")
$line.ChartArea="profile"; $line.ChartType="Line"; $line.BorderWidth=4
$line.Color=$blue; $line.MarkerStyle="Circle"; $line.MarkerSize=16
foreach($r in $data.profile) {[void]$line.Points.AddXY([double]$r.S,[double]$r.floor)}
[void]$c.Series.Add($line)
$hi=New-Object Windows.Forms.DataVisualization.Charting.Series("重点层")
$hi.ChartArea="profile"; $hi.ChartType="Point"; $hi.MarkerStyle="Circle"; $hi.MarkerSize=25
$hi.Color=$orange; $hi.Font=Font 25 $true
foreach($r in $data.profile | Where-Object {$_.floor -eq 5 -or $_.floor -eq 12}) {
    $i=$hi.Points.AddXY([double]$r.S,[double]$r.floor)
    $p=$hi.Points[$i]
    $p.Label=if($r.floor -eq 5) {"第5层  S = 2.132"} else {"屋顶  S = 11.724"}
    $p.LabelForeColor=$ink; $p.LabelBackColor=[Drawing.Color]::White
    $p["LabelStyle"]=if($r.floor -eq 5) {"Right"} else {"Left"}
}
[void]$c.Series.Add($hi)
Title $c "S越小，基准附近改善越慢；每层按本层基准剪力峰值归一。" 22 0 94 100 4
Export $c "figure1-S-along-height"

# Figure 2: same seven mode IDs in both panels, then all remaining293.
$c=Chart 1700
Title $c "同一基准控制峰的模态改善贡献" 32 0 1 100 5 $true
Title $c "SHW3X · 正值促进下降，负值抵消下降" 22 0 7 100 4
$legend=New-Object Windows.Forms.DataVisualization.Charting.Legend("effect")
$legend.Position=New-Object Windows.Forms.DataVisualization.Charting.ElementPosition(27,11,46,4)
$legend.Font=Font 21; $legend.LegendStyle="Row"; $legend.Alignment="Center"
$legend.BackColor=[Drawing.Color]::White
foreach($item in @(@("促进下降",$blue),@("抵消下降",$orange))) {
    $li=New-Object Windows.Forms.DataVisualization.Charting.LegendItem
    $li.Name=$item[0]; $li.Color=$item[1]; $li.ImageStyle="Rectangle"
    [void]$legend.CustomItems.Add($li)
}
[void]$c.Legends.Add($legend)
foreach($panel in @(@("Story5","left",1,"第5层  S = 2.132"),@("Story12","right",51,"屋顶（第12层）  S = 11.724"))) {
    $story=$panel[0]; $name=$panel[1]; $x=[single]$panel[2]
    Title $c $panel[3] 25 $x 16 48 5 $true
    $a=Area $c $name $x 22 48 65
    $a.InnerPlotPosition=New-Object Windows.Forms.DataVisualization.Charting.ElementPosition(24,1,73,83)
    $a.AxisX.Minimum=0.5; $a.AxisX.Maximum=8.5; $a.AxisX.Interval=1; $a.AxisX.IsReversed=$true
    $a.AxisX.MajorGrid.Enabled=$false; $a.AxisX.MajorTickMark.Enabled=$false; $a.AxisX.LineWidth=0
    $a.AxisY.Minimum=-4; $a.AxisY.Maximum=10; $a.AxisY.Interval=2
    $a.AxisY.Title="c（降幅%/阻尼百分点）"
    $a.AxisY.LabelStyle.Format="0"
    $zero=New-Object Windows.Forms.DataVisualization.Charting.StripLine
    $zero.IntervalOffset=0; $zero.StripWidth=0; $zero.BorderColor=$ink; $zero.BorderWidth=2
    [void]$a.AxisY.StripLines.Add($zero)
    $series=New-Object Windows.Forms.DataVisualization.Charting.Series($name)
    $series.ChartArea=$name; $series.ChartType="Bar"; $series.IsVisibleInLegend=$false
    $series["PointWidth"]="0.55"; $series["BarLabelStyle"]="Outside"
    $series.Font=Font 21; $j=0
    foreach($r in $data.bars | Where-Object {$_.Story -eq $story}) {
        $j++; $v=[double]$r.c
        $i=$series.Points.AddXY([double]$j,$v); $point=$series.Points[$i]
        $point.AxisLabel=$r.group; $point.Color=if($v -ge 0) {$blue} else {$orange}
        $point.Label=$v.ToString("+0.000;-0.000;0.000",[Globalization.CultureInfo]::InvariantCulture)
        $point.LabelForeColor=$ink
    }
    [void]$c.Series.Add($series)
}
Title $c "控制峰：第5层22.92 s，屋顶21.18 s。7阶并集＋其余293阶，各层有符号和为S。" 21 0 90 100 4
Title $c "c为基准峰值导数贡献，不是候选阻尼下实际剪力的模态分担。" 21 0 95 100 3.5
Export $c "figure2-signed-modal-improvement"
