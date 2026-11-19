# variáveis
#   indicadores_nj  indicadores por UF e faixa de intensidade digital  (135, 13)
#   perfil_nj       participação da faixa no valor adicionado da UF    (27, 5)
#   origem_nb       participação da origem nos insumos da faixa alta   (27, 3)
# dimensões
#   n = UFs (27) | j = faixas de intensidade digital (5)
#   b = origens dos insumos (3) | ano da MIP = 2018

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# 1. Ler os indicadores publicados e conferir as bases dos dois gráficos.
pasta = Path(__file__).resolve().parent
indicadores_nj = pd.read_csv(pasta / "indicadores_uf_2018.csv")
faixas = ["alta", "media_alta", "media_baixa", "baixa", "sem_classificacao"]
cores_faixa = ["#173f78", "#317fb4", "#73b3cf", "#bdcfdd", "#d9d9d9"]
assert indicadores_nj.shape == (135, 13)
assert indicadores_nj["ano"].eq(2018).all()
assert not indicadores_nj.duplicated(["uf", "intensidade_digital"]).any()
perfil_nj = indicadores_nj.pivot(index="uf", columns="intensidade_digital",
                                  values="participacao_na_uf_pct")[faixas]
assert perfil_nj.shape == (27, 5)
assert np.allclose(perfil_nj.sum(axis=1), 100)
ufs = perfil_nj["alta"].sort_values(ascending=False).index
perfil_nj = perfil_nj.loc[ufs]

# 2. Mostrar a composição do valor adicionado de cada UF por intensidade.
fig, ax = plt.subplots(figsize=(10, 10), layout="constrained")
esquerda_n = np.zeros(len(ufs))
for faixa, cor in zip(faixas, cores_faixa):
    parcela_n = perfil_nj[faixa].to_numpy()
    ax.barh(ufs, parcela_n, left=esquerda_n, height=0.75, label=faixa.replace("_", " "),
            color=cor, edgecolor="white", linewidth=0.35)
    esquerda_n += parcela_n
ax.bar_label(ax.containers[0], fmt="%.1f%%", label_type="center", color="white", fontsize=8)
ax.invert_yaxis()
ax.set(xlim=(0, 100), xlabel="Participação no valor adicionado da UF (%)",
       title="Valor adicionado por intensidade digital — UFs, 2018")
ax.set_axisbelow(True)
ax.grid(axis="x", alpha=0.2)
ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01), frameon=False)
fig.savefig(pasta / "valor_adicionado_intensidade_uf_2018.png", dpi=170)
plt.close(fig)

# 3. Mostrar a origem dos insumos consumidos pelas atividades de alta intensidade.
origem_nb = indicadores_nj.loc[indicadores_nj["intensidade_digital"].eq("alta")]
origem_nb = origem_nb.set_index("uf").loc[ufs,
    ["propria_uf_pct", "outras_ufs_pct", "importados_pct"]]
assert origem_nb.shape == (27, 3)
assert origem_nb.notna().all().all()
assert np.allclose(origem_nb.sum(axis=1), 100)
fig, ax = plt.subplots(figsize=(10, 10), layout="constrained")
esquerda_n = np.zeros(len(ufs))
for coluna, rotulo, cor in zip(origem_nb.columns,
                               ["Própria UF", "Outras UFs", "Importados"],
                               ["#28785c", "#e3a943", "#a94949"]):
    parcela_n = origem_nb[coluna].to_numpy()
    ax.barh(ufs, parcela_n, left=esquerda_n, height=0.75, label=rotulo,
            color=cor, edgecolor="white", linewidth=0.35)
    esquerda_n += parcela_n
ax.invert_yaxis()
ax.set(xlim=(0, 100), xlabel="Participação nos insumos consumidos (%)",
       title="Origem dos insumos das atividades de alta intensidade digital — UFs, 2018")
ax.set_axisbelow(True)
ax.grid(axis="x", alpha=0.2)
ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01), frameon=False)
fig.savefig(pasta / "origem_insumos_alta_intensidade_uf_2018.png", dpi=170)
plt.close(fig)
