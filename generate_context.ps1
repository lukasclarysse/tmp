# will generate context you can paste into ai
$ErrorActionPreference = "Stop"

$root = (Get-Location).Path
$output = Join-Path $root "project_context.txt"

$excludeDirectories = @(
    ".venv",
    "__pycache__",
    ".git",
    "uploads",
    "instance",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode"
)

$excludeFiles = @(
    ".env",
    ".env.local",
    "project_context.txt",
    "project_dump.txt",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.pyc"
)

$allowedExtensions = @(
    ".py", ".html", ".css", ".js",
    ".json", ".yaml", ".yml", ".toml",
    ".txt", ".md", ".sql", ".ini", ".cfg"
)

$files = Get-ChildItem -Path $root -Recurse -File |
    Where-Object {

        $relativePath = $_.FullName.Substring(
            $root.Length
        ).TrimStart('\', '/')

        $parts = $relativePath -split '[\\/]'

        $excludedDirectory = $false

        foreach ($part in $parts) {
            if ($excludeDirectories -contains $part) {
                $excludedDirectory = $true
                break
            }
        }

        $excludedFile = $false

        foreach ($pattern in $excludeFiles) {
            if ($_.Name -like $pattern) {
                $excludedFile = $true
                break
            }
        }

        -not $excludedDirectory -and
        -not $excludedFile -and
        $_.Extension -in $allowedExtensions -and
        $_.FullName -ne $output -and
        $_.Length -lt 500KB
    } |
    Sort-Object FullName

$tree = $files | ForEach-Object {
    $_.FullName.Substring($root.Length).TrimStart('\', '/')
}

$content = @()

$content += "============================================================"
$content += "PROJECT CONTEXT"
$content += "============================================================"
$content += ""
$content += "Project: DocuFix"
$content += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$content += "Root: $root"
$content += ""
$content += "PURPOSE:"
$content += "AI-powered document proofreading application using Flask,"
$content += "Ollama and Python."
$content += ""
$content += "PROJECT FILE TREE:"
$content += "------------------------------------------------------------"
$content += $tree
$content += ""
$content += "============================================================"
$content += "SOURCE FILE CONTENTS"
$content += "============================================================"

foreach ($file in $files) {

    $relativePath = $file.FullName.Substring(
        $root.Length
    ).TrimStart('\', '/')

    $content += ""
    $content += "============================================================"
    $content += "FILE: $relativePath"
    $content += "============================================================"

    try {
        $content += Get-Content -LiteralPath $file.FullName -Raw
    }
    catch {
        $content += "[Could not read file: $($_.Exception.Message)]"
    }
}

$content | Out-File `
    -LiteralPath $output `
    -Encoding utf8

Write-Host ""
Write-Host "Context dump created successfully!" -ForegroundColor Green
Write-Host "Output: $output"
Write-Host "Files included: $($files.Count)"
Write-Host "Size: $([math]::Round((Get-Item $output).Length / 1KB, 2)) KB"
