# ARRANQUE DO SINTONIA — a Sala, o vigia, o observador e o bot voltam sozinhos no logon.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File arranque_sintonia.ps1 [-UmaVolta] [-SimularEgresso BLOCKED]
#
# Missao BC3 (23/09/2026). Depois da tela azul das ~13 h, a Sala real, o supervisor do bot
# e o observador da ponte so voltaram a mao. Este script e o que a Tarefa Agendada
# «SINTONIA-Arranque» corre no logon. Ordem, e porque:
#
#   1. SALA (54330)        ligar_sala.cmd se nao responder; espera o pg_isready
#   2. VIGIA DA VPN        so avisa (vigia-vpn.log); lancado se nao estiver a correr
#   3. OBSERVADOR          le o disco, nao vai a rede: arranca sem esperar o egresso
#   4. PORTAO DE EGRESSO   o bot vai a rede (discovery, canarios): o supervisor SO arranca
#                          com superficie/rede.py --portao-de-egresso IT = PASS
#   5. SUPERVISOR          so se o proprio --estado disser que nao esta vivo (o lock dele
#                          e a segunda trava contra duas instancias)
#   6. GUARDA              de 3 em 3 min mede o egresso; 2 medicoes seguidas fora de IT ->
#                          PARAR.flag com a marca desta guarda (o bot fica quieto pelo
#                          procedimento da casa); 2 medicoes SEGUIDAS em IT -> tira SO o flag
#                          que ela escreveu e relanca o supervisor. Flag de outra mao nao se toca.
#
#   IT so conta com DUAS medicoes seguidas, a entrada e na guarda. Medido na BC3 (23/09,
#   18:30): com a VPN a oscilar, uma medicao IT isolada relancou o bot e as 4 seguintes
#   deram BR.
#
# Uma so instancia: mutex «SINTONIA-ARRANQUE». A segunda sai logo, e diz porque.
# -UmaVolta: faz 1-5 e sai (para provar). -SimularEgresso: finge o veredito do portao
# (so para provar que o supervisor NAO arranca fora de IT; nao toca na rede).

param([switch]$UmaVolta, [string]$SimularEgresso = "")

$ErrorActionPreference = "Continue"
$U      = $env:USERPROFILE
$VIVA   = "$U\orca\workspaces\eame-sintonia\source-curator-service-v1"
$CASA   = "$U\orca\workspaces\eame-sintonia\ponte-viva"
$SALA   = "$U\sintonia-sala-italia"
$PGBIN  = "$U\orca\pgtmp\pgsql\bin"
$PY     = "$U\AppData\Local\Programs\Python\Launcher\py.exe"
$BASH   = "C:\Program Files\Git\bin\bash.exe"
$VIGIA  = "$U\orca-tools\vigia_vpn.sh"
$LOGDIR = "$U\auditoria-madrugada"
$LOG    = Join-Path $LOGDIR ("arranque-" + (Get-Date -Format "yyyyMMdd") + ".log")
$MARCA  = "guarda-egresso do arranque_sintonia"
$FLAG   = "$VIVA\curadoria\PARAR.flag"

function L([string]$m) {
    $linha = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
    Add-Content -Path $LOG -Value $linha -Encoding UTF8
    Write-Output $linha
}

function Procs([string]$padrao) {
    @(Get-CimInstance Win32_Process -Filter "Name='python.exe' or Name='py.exe' or Name='bash.exe'" |
      Where-Object { $_.CommandLine -and $_.CommandLine -match $padrao })
}

function SalaPronta { & "$PGBIN\pg_isready.exe" -h 127.0.0.1 -p 54330 *> $null; return ($LASTEXITCODE -eq 0) }

function Egresso {
    if ($SimularEgresso) { return $SimularEgresso }
    Push-Location $VIVA
    $env:PYTHONUTF8 = "1"
    $txt = (& $PY -X utf8 superficie/rede.py --portao-de-egresso IT 2>$null) -join ""
    Pop-Location
    if ($txt -match '"EGRESS_GATE":\s*"([A-Z]+)"') { $g = $Matches[1] } else { $g = "UNKNOWN" }
    if ($txt -match '"EGRESS_COUNTRY_CODE":\s*"([A-Z]+)"') { $c = $Matches[1] } else { $c = "?" }
    return "$g $c"
}

function SupervisorVivo {
    Push-Location $VIVA
    $txt = (& $PY -X utf8 curadoria/supervisor.py --estado 2>$null) -join ""
    Pop-Location
    return ($txt -match '"SUPERVISOR_ALIVE":\s*true')
}

function LancarSupervisor {
    if (SupervisorVivo) { L "SUPERVISOR ja vivo (o --estado dele diz SUPERVISOR_ALIVE): nao se lanca outro"; return }
    if (Test-Path $FLAG) {
        $quem = (Get-Content $FLAG -Raw -ErrorAction SilentlyContinue)
        if ($quem -notmatch [regex]::Escape($MARCA)) {
            L "SUPERVISOR nao lancado: ha um PARAR.flag de OUTRA mao ($($quem.Trim())) — nao se toca"; return
        }
        Remove-Item $FLAG -Force; L "PARAR.flag da guarda retirado"
    }
    Start-Process powershell -WindowStyle Minimized -ArgumentList @(
        "-NoLogo", "-NoExit", "-Command", "Set-Location '$VIVA'; & '$PY' curadoria/supervisor.py")
    Start-Sleep -Seconds 8
    L ("SUPERVISOR lancado; vivo agora: " + (SupervisorVivo))
}

# --- uma so instancia ----------------------------------------------------------------
New-Item -ItemType Directory -Force -Path $LOGDIR | Out-Null
$mutex = New-Object System.Threading.Mutex($false, "SINTONIA-ARRANQUE")
if (-not $mutex.WaitOne(0)) { L "ARRANQUE ja a correr noutra instancia: esta sai sem fazer nada"; exit 0 }

try {
    L "=== ARRANQUE (UmaVolta=$UmaVolta, SimularEgresso='$SimularEgresso') ==="

    # 1. SALA
    if (SalaPronta) { L "SALA ja responde em 54330" }
    else {
        L "SALA nao responde: ligar_sala.cmd"
        # SEM redireccionar a saida: o postmaster herda o handle e a espera nunca acaba
        # (medido na BC3: o arranque pendurou aqui). O pg_ctl ja escreve no postgres.log.
        Start-Process cmd.exe -WindowStyle Hidden -ArgumentList @("/c", "`"$SALA\ligar_sala.cmd`"")
        $ok = $false
        for ($i = 0; $i -lt 36; $i++) { if (SalaPronta) { $ok = $true; break }; Start-Sleep -Seconds 5 }
        L ("SALA pronta: $ok")
    }

    # 2. VIGIA DA VPN
    if ((Procs 'vigia_vpn\.sh').Count -gt 0) { L "VIGIA ja a correr" }
    else { Start-Process $BASH -WindowStyle Hidden -ArgumentList @($VIGIA); Start-Sleep -Seconds 2
           L ("VIGIA lancado; processos: " + (Procs 'vigia_vpn\.sh').Count) }

    # 3. OBSERVADOR
    if ((Procs 'ponte_automatica\.py --servir').Count -gt 0) { L "OBSERVADOR ja a correr" }
    else {
        Start-Process powershell -WindowStyle Minimized -ArgumentList @(
            "-NoLogo", "-NoExit", "-Command",
            "Set-Location '$CASA'; & '$PY' curadoria/ponte_automatica.py --servir --intervalo 20 --lane '$VIVA'")
        Start-Sleep -Seconds 5
        L ("OBSERVADOR lancado da casa $CASA; processos: " + (Procs 'ponte_automatica\.py --servir').Count)
    }

    # 4. PORTAO DE EGRESSO, 5. SUPERVISOR
    while ($true) {
        $e = Egresso
        L "EGRESSO $e"
        if ($e -like "PASS IT*") {
            Start-Sleep -Seconds 30
            $e2 = Egresso
            L "EGRESSO (2.a medicao) $e2"
            if ($e2 -like "PASS IT*") { LancarSupervisor; break }
        }
        L "SUPERVISOR NAO arranca: o egresso nao e IT (o bot iria a rede por outro pais)"
        if ($UmaVolta) { break }
        Start-Sleep -Seconds 60
    }
    if ($UmaVolta) { L "=== UmaVolta: fim ==="; exit 0 }

    # 6. GUARDA
    $ruins = 0; $bons = 0
    while ($true) {
        Start-Sleep -Seconds 180
        $e = Egresso
        if ($e -like "PASS IT*") {
            $bons++
            $flagDaGuarda = (Test-Path $FLAG) -and ((Get-Content $FLAG -Raw) -match [regex]::Escape($MARCA))
            if ($flagDaGuarda -or $ruins -ge 2) {
                if ($bons -ge 2) { L "GUARDA: egresso em IT ha $bons medicoes seguidas ($e)"; LancarSupervisor; $ruins = 0 }
                else { L "GUARDA: egresso IT ($e), 1.a medicao boa — espera a 2.a antes de relancar" }
            } else { $ruins = 0 }
        } else {
            $bons = 0
            $ruins++
            L "GUARDA: egresso $e ($ruins seguida(s))"
            if ($ruins -eq 2 -and -not (Test-Path $FLAG)) {
                Set-Content -Path $FLAG -Value "$MARCA $(Get-Date -Format s): egresso $e" -Encoding UTF8
                L "GUARDA: PARAR.flag escrito — o bot fica quieto ate o egresso voltar a IT"
            }
        }
    }
}
finally { $mutex.ReleaseMutex() | Out-Null; $mutex.Dispose() }
