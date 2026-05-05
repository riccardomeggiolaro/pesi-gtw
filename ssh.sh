Script diagnostica SSH
Da eseguire direttamente sul gateway Ubuntu (console fisica / KVM / accesso diretto)
Script completo — incolla su Ubuntu
#!/bin/bash
# ─────────────────────────────────────────────
#  SSH DIAGNOSTICS — Ubuntu Gateway
# ─────────────────────────────────────────────

echo "============================================"
echo " DIAGNOSTICA SSH GATEWAY"
echo "============================================"

# 1. Stato servizio SSH
echo ""
echo "[1] Stato servizio SSH"
echo "----------------------------------------------"
systemctl status ssh 2>/dev/null || systemctl status sshd 2>/dev/null || \
  echo "ERRORE: servizio ssh/sshd non trovato"

# 2. SSH installato?
echo ""
echo "[2] Pacchetto openssh-server"
echo "----------------------------------------------"
dpkg -l openssh-server 2>/dev/null | grep -E "^(ii|rc|un)" || \
  echo "NON INSTALLATO"

# 3. Porta e bind address in sshd_config
echo ""
echo "[3] Configurazione sshd_config (Port / ListenAddress)"
echo "----------------------------------------------"
grep -Ei "^(Port|ListenAddress)" /etc/ssh/sshd_config 2>/dev/null || \
  echo "(nessuna direttiva esplicita — default: porta 22, tutti gli IP)"

# 4. Su quale porta sta ascoltando SSH realmente?
echo ""
echo "[4] Porte in ascolto (SSH)"
echo "----------------------------------------------"
ss -tlnp | grep -E ":(22|ssh)" || echo "Nessun processo ascolta sulla porta 22"

# 5. IP configurati sul server
echo ""
echo "[5] Indirizzi IP del gateway"
echo "----------------------------------------------"
ip -4 addr show | grep -E "inet " | awk '{print $2, $NF}'

# 6. Regole UFW
echo ""
echo "[6] Regole UFW attive"
echo "----------------------------------------------"
ufw status verbose 2>/dev/null || echo "UFW non attivo o non installato"

# 7. Firewall iptables (raw)
echo ""
echo "[7] Regole iptables INPUT (porta 22)"
echo "----------------------------------------------"
iptables -L INPUT -n --line-numbers 2>/dev/null | grep -E "(22|ssh|DROP|REJECT|ACCEPT)" || \
  echo "(nessuna regola rilevante trovata)"

echo ""
echo "============================================"
echo " FINE DIAGNOSTICA"
echo "============================================"
echo ""
echo "--- AZIONI AUTOMATICHE ---"

# Tenta di avviare SSH se non attivo
if ! systemctl is-active --quiet ssh 2>/dev/null && \
   ! systemctl is-active --quiet sshd 2>/dev/null; then
  echo "[!] SSH non attivo — provo ad avviarlo..."
  if dpkg -l openssh-server 2>/dev/null | grep -q "^ii"; then
    systemctl start ssh && echo "[OK] SSH avviato con successo" || \
    echo "[FAIL] Impossibile avviare SSH"
  else
    echo "[!] openssh-server non installato — installo..."
    apt-get install -y openssh-server && \
    systemctl enable --now ssh && \
    echo "[OK] SSH installato e avviato" || \
    echo "[FAIL] Installazione fallita"
  fi
else
  echo "[OK] SSH risulta attivo — nessuna azione necessaria"
fi