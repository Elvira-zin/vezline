@echo off
EnableDelayedExpansion

for /f "usebackq tokens=1,* delims==" %%A in ("config\docker\.env") do (
    if not "%%A"=="" (
        set "%%A=%%B"
    )
)


echo POSTGRES_DB: !POSTGRES_DB!
echo POSTGRES_USER: !POSTGRES_USER!
echo POSTGRES_PASSWORD: !POSTGRES_PASSWORD!