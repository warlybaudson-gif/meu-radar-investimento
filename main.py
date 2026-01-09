import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import os  # Para o alerta sonoro (funciona em Windows, Mac e Linux)

class IARockefellerV4:
    def __init__(self):
        # 1. BASE ORIGINAL
        self.base_xp = {"patrimonio_inicial": 50.00, "rentabilidade_fixa": -0.11}

        # 2. QUANTIDADES (Ajuste conforme sua posse)
        self.ativos = {
            "nvidia_qty": 10,
            "ouro_gramas": 50.0,
            "minerais_valor_estimado": 5000.00
        }

        # 3. DEFINIÇÃO DE ALERTAS (Ajuste seus alvos aqui)
        self.alvos = {
            "nvidia_brl_alvo": 850.00,  # Alerta se Nvidia passar de R$ 850
            "ouro_g_brl_alvo": 800.00    # Alerta se Grama do Ouro passar de R$ 800
        }

    def disparar_alerta(self, mensagem):
        print(f"\n⚠️  [ALERTA ROCKEFELLER] {mensagem}")
        # Emite um sinal sonoro (compatível com a maioria dos sistemas)
        for _ in range(3):
            print('\a') # Código de sistema para "Beep"
            time.sleep(0.5)

    def fetch_data(self):
        try:
            data = yf.download(["NVDA", "GC=F", "USDBRL=X"], period="1d", interval="1m", progress=False)
            cambio = data['Close']['USDBRL=X'].iloc[-1]
            # Conversão: Oz para Grama (31.1035) e USD para BRL
            precos = {
                "nvda": data['Close']['NVDA'].iloc[-1] * cambio,
                "ouro_g": (data['Close']['GC=F'].iloc[-1] / 31.1035) * cambio,
                "dolar": cambio
            }
            return precos
        except:
            return None

    def executar(self):
        precos = self.fetch_data()
        if not precos: return

        val_nvda = self.ativos["nvidia_qty"] * precos["nvda"]
        val_joias = self.ativos["ouro_gramas"] * precos["ouro_g"]
        total = self.base_xp["patrimonio_inicial"] + val_nvda + val_joias + self.ativos["minerais_valor_estimado"]

        # LOGICA DE ALERTA
        if precos["nvda"] >= self.alvos["nvidia_brl_alvo"]:
            self.disparar_alerta(f"NVIDIA ATINGIU O ALVO! Cotação atual: R$ {precos['nvda']:.2f}")
        
        if precos["ouro_g"] >= self.alvos["ouro_g_brl_alvo"]:
            self.disparar_alerta(f"OURO ATINGIU O ALVO! Cotação atual: R$ {precos['ouro_g']:.2f}")

        # DASHBOARD
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] PATRIMÔNIO CONSOLIDADO: R$ {total:,.2f}")
        print(f"Nvidia: R$ {val_nvda:,.2f} | Ouro: R$ {val_joias:,.2f} | Dólar: R$ {precos['dolar']:.2f}")

# --- START ---
if __name__ == "__main__":
    app = IARockefellerV4()
    print("Iniciando Monitoramento com Alertas... Pressione Ctrl+C para parar.")
    try:
        while True:
            app.executar()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nIA Rockefeller em repouso.")
