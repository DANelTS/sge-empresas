# instalar.ps1 — deja el entorno de trabajo listo en Windows.
#
#   .\instalar.ps1                                        solo el entorno
#   .\instalar.ps1 -Sector cerveceria -Alumno 7           además, genera la variante
#   .\instalar.ps1 -Sector _demo-tostadero -Alumno 0 -Completo   demo lista (profesor)
#
# Con -Completo también importa los maestros, configura la compañía, carga el
# histórico y verifica. Es el camino del profesor para ensayar la demo.
#
# Si PowerShell se queja de la política de ejecución:
#   powershell -ExecutionPolicy Bypass -File .\instalar.ps1 ...

[CmdletBinding()]
param(
    [string]$Sector = "",
    [int]$Alumno = -1,
    [switch]$Completo,
    [string]$Bd = "empresa"
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Paso($texto) { Write-Host "`n== $texto" -ForegroundColor Cyan }
function Bien($texto) { Write-Host "  $texto" -ForegroundColor Green }
function Mal($texto)  { Write-Host "  $texto" -ForegroundColor Red }

function Nueva-Clave {
    $letras = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    -join (1..24 | ForEach-Object { $letras[(Get-Random -Maximum $letras.Length)] })
}

# ---------------------------------------------------------------------------
Paso "1. Comprobando Docker"
# ---------------------------------------------------------------------------
try {
    docker compose version | Out-Null
} catch {
    Mal "No encuentro 'docker compose'."
    Write-Host "  Instala Docker Desktop y ábrelo antes de ejecutar este script."
    exit 1
}
try {
    docker info | Out-Null
} catch {
    Mal "El motor de Docker no responde. ¿Está Docker Desktop arrancado?"
    exit 1
}
Bien "Docker y compose disponibles"

# ---------------------------------------------------------------------------
Paso "2. Configuración de Odoo (config\odoo.conf)"
# ---------------------------------------------------------------------------
if (Test-Path "config\odoo.conf") {
    Bien "config\odoo.conf ya existe; no lo toco"
} else {
    Copy-Item "config\odoo.conf.example" "config\odoo.conf"
    Bien "config\odoo.conf creado a partir del ejemplo"
    Write-Host "  Si quieres, cambia dentro la contraseña maestra (admin_passwd)."
}

# Puerto publicado en docker-compose.yml (127.0.0.1:8069:8069). Si lo cambias
# allí, cambia también esta línea.
$puerto = "8069"

# ---------------------------------------------------------------------------
Paso "3. Arrancando PostgreSQL y Odoo"
# ---------------------------------------------------------------------------
docker compose up -d
Write-Host -NoNewline "  Esperando a que Odoo responda"
$listo = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        Invoke-WebRequest -Uri "http://localhost:$puerto/web/login" -UseBasicParsing -TimeoutSec 3 | Out-Null
        $listo = $true
        break
    } catch {
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 3
    }
}
Write-Host ""
if (-not $listo) {
    Mal "Odoo no responde. Mira el registro:"
    Write-Host "    docker compose logs --tail 50 odoo"
    exit 1
}
Bien "Odoo en marcha en http://localhost:$puerto"

# ---------------------------------------------------------------------------
Paso "4. Base de datos '$Bd'"
# ---------------------------------------------------------------------------
$lineaClave = Select-String -Path "config\odoo.conf" -Pattern '^admin_passwd' | Select-Object -First 1
$clave = ($lineaClave.Line -split "=", 2)[1].Trim()

$existe = $false
try {
    $bases = docker compose exec -T db psql -U odoo -lqt
    $existe = ($bases | ForEach-Object { ($_ -split '\|')[0].Trim() }) -contains $Bd
} catch {
    $existe = $false
}

if ($existe) {
    Bien "La base '$Bd' ya existe"
} else {
    Write-Host "  Creando la base (país España, idioma español)…"
    docker compose run --rm odoo odoo db init $Bd --country ES --language es_ES --username admin --password $clave | Out-Null
    Write-Host "  Instalando CRM, Ventas, Compras, Inventario y Facturación…"
    docker compose run --rm odoo odoo module install -d $Bd account sale_management purchase stock crm | Out-Null
    Bien "Base creada con la localización española"
}

# ---------------------------------------------------------------------------
if ($Sector -ne "") {
    if ($Alumno -lt 0) { $Alumno = 0 }
    $codigo = "{0:D2}" -f $Alumno
    Paso "5. Generando la variante $Sector A$codigo"
    docker compose run --rm herramientas generar.py --empresa $Sector --alumno $Alumno
}

# ---------------------------------------------------------------------------
if ($Completo) {
    Paso "6. Cargando datos (camino del profesor)"
    if ($Sector -eq "") { $Sector = "_demo-tostadero"; $Alumno = 0 }
    $comun = @("--empresa", $Sector, "--alumno", "$Alumno", "--bd", $Bd, "--url", "http://odoo:8069")
    docker compose run --rm herramientas importar_maestros.py @comun
    docker compose run --rm herramientas configurar_compania.py @comun
    docker compose run --rm herramientas cargar_historico.py @comun
    docker compose run --rm herramientas verificar.py @comun
}

# ---------------------------------------------------------------------------
Paso "Listo"
# ---------------------------------------------------------------------------
Write-Host "  Odoo:     http://localhost:$puerto  (usuario admin)"
Write-Host "  Base:     $Bd"
if ($Sector -ne "") {
    $codigo = "{0:D2}" -f $Alumno
    Write-Host "  Variante: salida\$Sector-A$codigo\"
    Write-Host "  Siguiente paso: abre su LEEME.md e importa los CSV en Odoo."
}
Write-Host ""
Write-Host "  Parar el entorno:  docker compose down"
Write-Host "  Ver el registro:   docker compose logs -f odoo"
