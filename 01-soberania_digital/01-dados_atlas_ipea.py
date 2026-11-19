# variáveis
#   mip            planilha MIP-Ir do Atlas Econômico do Ipea   (1864, 2003)
#   VA_dnj         componentes do valor adicionado              (8, 27, 68)
#   CI_nac_inj     insumos nacionais por UF de origem/destino   (27, 27, 68)
#   CI_bnj         insumos nacionais/importados por destino    (2, 27, 68)
#   uf_n           UFs na ordem da planilha                     (27,)
#   nome_j         atividades na ordem da planilha              (68,)
# dimensões
#   d = componentes do valor adicionado (8) | b = origens (2)
#   i = UF fornecedora (27) | n = UF compradora (27)
#   j = atividades TRU68 (68) | ano da MIP = 2018

import os
from pathlib import Path

import numpy as np
import pandas as pd


# 1. Ler a planilha MIP-Ir de 2018 compartilhada pelo Felipe.
# Site de origem: https://www.ipea.gov.br/atlaseconomico/
# Link da cópia: https://docs.google.com/spreadsheets/d/1R9Vmk1ZalwWB6QUt-_MJKfA67VFSRTlS/edit
# Compartilhada em 2026-11-19; data do download original não informada.
pasta = Path(__file__).resolve().parent
entrada = os.environ.get(
    "IPEA_MIP_XLSX",
    "https://docs.google.com/spreadsheets/d/"
    "1R9Vmk1ZalwWB6QUt-_MJKfA67VFSRTlS/export?format=xlsx",
)
saida = Path(os.environ.get("IPEA_DADOS_NPZ", pasta / "dados_mip_2018.npz"))
mip = pd.read_excel(entrada, header=None)
assert mip.shape == (1864, 2003), f"Formato inesperado da MIP-Ir: {mip.shape}"

# 2. Extrair UFs e atividades dos cabeçalhos, conferindo todas as regiões.
uf_n = mip.iloc[0, 2:1838:68].to_numpy(dtype=str)
nome_j = mip.iloc[1, 2:70].to_numpy(dtype=str)
assert uf_n.shape == (27,) and nome_j.shape == (68,)
assert np.array_equal(mip.iloc[0, 2:1838].ffill().to_numpy(), np.repeat(uf_n, 68))
assert np.array_equal(mip.iloc[1, 2:1838].to_numpy().reshape(27, 68),
                      np.broadcast_to(nome_j, (27, 68)))
assert np.array_equal(mip.iloc[3:1839, 0].ffill().to_numpy(), np.repeat(uf_n, 68))
assert np.array_equal(mip.iloc[3:1839, 1].to_numpy().reshape(27, 68),
                      np.broadcast_to(nome_j, (27, 68)))

# 3. Reproduzir os recortes documentados na matriz original do Ipea.
# 3.1. A terceira linha da planilha é um cabeçalho extra.
mip = mip.drop(index=2).reset_index(drop=True)
# 3.2. As primeiras 1836 linhas e colunas numéricas são as 27 UFs x 68 atividades.
CI_nac_iknj = mip.iloc[2:1838, 2:1838].to_numpy(dtype=float).reshape(27, 68, 27, 68)
CI_nac_inj = CI_nac_iknj.sum(axis=1)
CI_bnj = mip.iloc[1838:1840, 2:1838].to_numpy(dtype=float).reshape(2, 27, 68)
# 3.3. Oito linhas da planilha compõem o valor adicionado.
linhas_va = [1849, 1851, 1852, 1853, 1855, 1856, 1858, 1859]
VA_dnj = mip.iloc[linhas_va, 2:1838].to_numpy(dtype=float).reshape(8, 27, 68)
assert np.allclose(CI_nac_inj.sum(axis=0), CI_bnj[0])
assert np.isfinite(VA_dnj).all() and np.isfinite(CI_bnj).all()

# 4. Gravar as matrizes e os rótulos na mesma ordem da planilha.
saida.parent.mkdir(parents=True, exist_ok=True)
np.savez_compressed(saida, VA_dnj=VA_dnj, CI_nac_inj=CI_nac_inj,
                    CI_bnj=CI_bnj, uf_n=uf_n, nome_j=nome_j)
print(f"Gerado: {saida}")
