# variáveis
#   VA_dnj       componentes do valor adicionado por UF e atividade   (8, 27, 68)
#   CI_nac_inj   insumos nacionais por UF de origem e destino         (27, 27, 68)
#   CI_bnj       insumos nacionais/importados por destino             (2, 27, 68)
#   va_nj        valor adicionado por UF e atividade                  (27, 68)
#   origem_in    insumos nacionais por UF de origem e destino        (27, 27)
#   uf_n         UFs extraídas da planilha                           (27,)
#   codigo_j     códigos TRU68 na ordem das atividades               (68,)
#   nome_j       nomes extraídos da planilha                          (68,)
# dimensões
#   d = componentes do valor adicionado (8) | b = origens (2)
#   i = UF de origem (27) | k = atividade de origem (68)
#   n = UF de destino (27) | j = atividade de destino (68)
#   ano da MIP = 2018

import os
from pathlib import Path

import numpy as np
import pandas as pd


# 1. Carregar as matrizes extraídas da planilha oficial do Atlas Econômico.
pasta = Path(__file__).resolve().parent
entrada = Path(os.environ.get("IPEA_DADOS_NPZ", pasta / "dados_mip_2018.npz"))
# 1.1. Manter os códigos TRU68, ausentes do XLSX, na ordem das atividades.
codigo_j = ['0191',
 '0192',
 '0280',
 '0580',
 '0680',
 '0791',
 '0792',
 '1091',
 '1092',
 '1093',
 '1100',
 '1200',
 '1300',
 '1400',
 '1500',
 '1600',
 '1700',
 '1800',
 '1991',
 '1992',
 '2091',
 '2092',
 '2093',
 '2100',
 '2200',
 '2300',
 '2491',
 '2492',
 '2500',
 '2600',
 '2700',
 '2800',
 '2991',
 '2992',
 '3000',
 '3180',
 '3300',
 '3500',
 '3680',
 '4180',
 '4500',
 '4680',
 '4900',
 '5000',
 '5100',
 '5280',
 '5500',
 '5600',
 '5800',
 '5980',
 '6100',
 '6280',
 '6480',
 '6800',
 '6980',
 '7180',
 '7380',
 '7700',
 '7880',
 '8000',
 '8400',
 '8591',
 '8592',
 '8691',
 '8692',
 '9080',
 '9480',
 '9700']
# 1.2. Carregar matrizes, UFs e nomes extraídos do XLSX pelo primeiro script.
codigo_j = np.asarray(codigo_j)
with np.load(entrada) as dados:
    VA_dnj = dados["VA_dnj"]
    CI_nac_inj = dados["CI_nac_inj"]
    CI_bnj = dados["CI_bnj"]
    uf_n = dados["uf_n"]
    nome_j = dados["nome_j"]
assert uf_n.shape == (27,) and nome_j.shape == codigo_j.shape == (68,)
assert VA_dnj.shape == (8, 27, 68)
assert CI_nac_inj.shape == (27, 27, 68)
assert CI_bnj.shape == (2, 27, 68)
assert np.allclose(CI_nac_inj.sum(axis=0), CI_bnj[0])

# 2. Adaptar a classificação ISIC da OIT, anexo A2, à atividade TRU68.
# 2.1. Os dois primeiros dígitos do código TRU68 indicam a divisão ISIC/CNAE
# aproximada. As atividades 6280 e 7180 agregam divisões vizinhas, mas todas
# as divisões agregadas têm a mesma faixa. O código 9700 não consta do anexo.
faixa_por_divisao = {
    1: "baixa", 2: "baixa", 3: "baixa", 5: "baixa", 6: "baixa", 7: "baixa",
    10: "baixa", 11: "baixa", 12: "baixa", 13: "media_baixa",
    14: "media_baixa", 15: "media_baixa", 16: "media_alta",
    17: "media_alta", 18: "media_alta", 19: "media_baixa",
    20: "media_baixa", 21: "media_baixa", 22: "media_baixa",
    23: "media_baixa", 24: "media_baixa", 25: "media_baixa",
    26: "media_alta", 27: "media_alta", 28: "media_alta",
    29: "alta", 30: "alta", 31: "media_alta", 32: "media_alta",
    33: "media_alta", 35: "baixa", 36: "baixa", 37: "baixa",
    38: "baixa", 39: "baixa", 41: "baixa", 42: "baixa",
    43: "baixa", 45: "media_alta", 46: "media_alta",
    47: "media_alta", 49: "baixa", 50: "baixa", 51: "baixa",
    52: "baixa", 53: "baixa", 55: "baixa", 56: "baixa",
    58: "media_alta", 59: "media_alta", 60: "media_alta",
    61: "alta", 62: "alta", 63: "alta", 64: "alta", 65: "alta",
    66: "alta", 68: "baixa", 69: "alta", 70: "alta", 71: "alta",
    72: "alta", 73: "alta", 74: "alta", 75: "alta", 77: "alta",
    78: "alta", 79: "alta", 80: "alta", 81: "alta", 82: "alta",
    84: "media_alta", 85: "media_baixa", 86: "media_baixa",
    87: "media_baixa", 88: "media_baixa", 90: "media_alta",
    91: "media_alta", 92: "media_alta", 93: "media_alta",
    94: "alta", 95: "alta", 96: "alta",
}
divisao_j = np.array([int(c[:2]) for c in codigo_j])
faixa_j = np.array([faixa_por_divisao.get(d, "sem_classificacao") for d in divisao_j])
assert set(faixa_j) == {"baixa", "media_baixa", "media_alta", "alta", "sem_classificacao"}
assert codigo_j[faixa_j == "sem_classificacao"].tolist() == ["9700"]
pd.DataFrame({"codigo_tru68": codigo_j, "atividade_tru68": nome_j,
              "divisao_isic_aproximada": divisao_j, "intensidade_digital": faixa_j}).to_csv(
    pasta / "correspondencia_tru68_intensidade.csv", index=False)

# 3. Medir concentração por valor adicionado e origem dos insumos consumidos.
va_nj = VA_dnj.sum(axis=0)
assert np.all(np.isfinite(va_nj))
assert np.all(va_nj >= -1e-8)
va_total_n = va_nj.sum(axis=1)
linhas = []
for faixa in ("baixa", "media_baixa", "media_alta", "alta", "sem_classificacao"):
    máscara_j = (faixa_j == faixa).astype(float)
    va_n = np.einsum("nj,j->n", va_nj, máscara_j)
    origem_in = np.einsum("inj,j->in", CI_nac_inj, máscara_j)
    propria_n = np.diag(origem_in)
    outras_n = origem_in.sum(axis=0) - propria_n
    importada_n = np.einsum("nj,j->n", CI_bnj[1], máscara_j)
    consumo_n = propria_n + outras_n + importada_n
    assert np.allclose(origem_in.sum(axis=0), np.einsum("nj,j->n", CI_bnj[0], máscara_j))
    assert np.all(consumo_n >= 0)
    linhas.append(pd.DataFrame({
        "ano": 2018, "uf": uf_n, "intensidade_digital": faixa,
        "valor_adicionado": va_n,
        "participacao_na_faixa_brasil_pct": np.divide(100 * va_n, va_n.sum(),
                                                      out=np.full(27, np.nan), where=va_n.sum() != 0),
        "participacao_na_uf_pct": np.divide(100 * va_n, va_total_n,
                                            out=np.full(27, np.nan), where=va_total_n != 0),
        "insumos_propria_uf": propria_n, "insumos_outras_ufs": outras_n,
        "insumos_importados": importada_n, "insumos_total": consumo_n,
        "propria_uf_pct": np.divide(100 * propria_n, consumo_n,
                                     out=np.full(27, np.nan), where=consumo_n != 0),
        "outras_ufs_pct": np.divide(100 * outras_n, consumo_n,
                                     out=np.full(27, np.nan), where=consumo_n != 0),
        "importados_pct": np.divide(100 * importada_n, consumo_n,
                                     out=np.full(27, np.nan), where=consumo_n != 0),
    }))

# 4. Gravar os indicadores com uma linha por UF e faixa digital.
indicadores = pd.concat(linhas, ignore_index=True)
assert indicadores.shape[0] == 27 * 5
assert np.allclose(indicadores.groupby("uf").valor_adicionado.sum().to_numpy(),
                   pd.Series(va_total_n, index=uf_n).loc[sorted(uf_n)].to_numpy())
assert np.allclose(indicadores[["insumos_propria_uf", "insumos_outras_ufs",
                               "insumos_importados"]].sum(axis=1), indicadores.insumos_total)
indicadores.to_csv(pasta / "indicadores_uf_2018.csv", index=False, float_format="%.10f")
print("Gerados: correspondencia_tru68_intensidade.csv e indicadores_uf_2018.csv")
