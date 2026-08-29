#(C:\Users\Priyanka\miniconda3\shell\condabin\conda-hook.ps1) ; (conda activate spark)

Use these PowerShell commands

From your project folder:

Remove-Item -Recurse -Force .\__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\analytics\__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\services\__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\components\__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\utils\__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\pages\__pycache__ -ErrorAction SilentlyContinue

You can also remove all Python cache directories in the project at once:

Get-ChildItem -Path . -Directory -Filter "__pycache__" -Recurse |
    Remove-Item -Recurse -Force