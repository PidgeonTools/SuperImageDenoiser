$releaseDir = "SuperImageDenoiser"
$releaseZipFile = "$releaseDir.zip"
$excludePatterns = ($releaseDir, $releaseZipFile, "scripts", "__pycache__", ".git", ".vscode", "*_updater")
$basePath = $PSScriptRoot | Split-Path
$releasePath = Join-Path $basePath $releaseDir
$releaseZip = Join-Path $basePath $releaseZipFile

Write-Output "Creating release package for $releaseDir"
Write-Output ""

if (Test-Path $releasePath) {
    Write-Output "Deleting existing files in $releasePath ..."
    Remove-Item $releasePath -Recurse
    Write-Output ""
}

# thanks, https://stackoverflow.com/a/69964408 for the inspiration!
# plus some modifications by BeheadedKamikaze :)
function Copy-Folder {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [String] $FromPath,

        [Parameter(Mandatory)]
        [String] $ToPath,

        [string[]] $Exclude
    )

    if (Test-Path $FromPath -PathType Container) {
        # skip if directory is empty
        if ((Get-ChildItem $FromPath -Force | Select-Object -First 1 | Measure-Object).Count -eq 0) {
            return
        }

        # create target directory
        New-Item $ToPath -ItemType Directory -ErrorAction SilentlyContinue | Out-Null

        # copy contents
        Get-ChildItem $FromPath -Force | ForEach-Object {
            # capture the pipeline variable
            $item = $_
            $target_path = Join-Path $ToPath $item.Name
            if (($Exclude | ForEach-Object { $item.Name -like $_ }) -notcontains $true) {
                # delete target if it exists
                if (Test-Path $target_path) { Remove-Item $target_path -Recurse -Force }
                if ($item.PSIsContainer) {
                    # recursively copy subdirectories
                    Copy-Folder -FromPath $item.FullName -ToPath $target_path -Exclude $Exclude
                } else {
                    Copy-Item $item.FullName $target_path
                }
            }
        }
    }
}

Write-Output "Copying files from $basePath to $releasePath ..."
Copy-Folder -FromPath $basePath -ToPath $releasePath -Exclude $excludePatterns

Write-Output ""
Write-Output "Files copied OK."
Write-Output ""

if (Test-Path $releaseZip) {
    Write-Output "Deleting existing release zip file $releaseZip"
    Remove-Item $releaseZip
    Write-Output ""
}

Write-Output "Compressing files to $releaseZip ..."

[Reflection.Assembly]::LoadWithPartialName("System.IO.Compression.FileSystem")
[System.IO.Compression.ZipFile]::CreateFromDirectory($releasePath, $releaseZip, [System.IO.Compression.CompressionLevel]::Optimal, $true)

Write-Output ""
Write-Output "Compressed files OK."
Write-Output ""
Write-Output "Cleaning up..."
Remove-Item $releasePath -Recurse

Write-Output ""
Write-Output "All done! You can now create a new release and attach $releaseZip"

Pause
