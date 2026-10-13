. { param() } 
$src = Get-Content -Raw ./apply_patches.ps1
$start = $src.IndexOf('function RU32'); 
