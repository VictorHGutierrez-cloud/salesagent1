import pandas as pd

# Criar os dados em formato de tabela
data = {
    "Módulos": ["Base + ATS", "Base + ATS"],
    "Nº Colaboradores": [2500, 800],
    "Valor por Vida (R$)": [9.00, 11.00],
    "Fixo Recrutamento (R$)": [650.00, 1000.00],
    "Total Vidas (R$)": [25750.00, 8800.00],
    "Bases de Recrutamento": [5, 1]
}

# Criar DataFrame
df = pd.DataFrame(data)

# Adicionar coluna com Total Geral (Total Vidas + Fixo)
df["Total Geral (R$)"] = df["Total Vidas (R$)"] + df["Fixo Recrutamento (R$)"]

# Salvar em Excel no diretório do projeto
file_path = r"C:\Users\victo\Sales Agent\planilha_recrutamento.xlsx"
df.to_excel(file_path, index=False)

print(f"Planilha salva com sucesso em: {file_path}")
print("\nDados da planilha:")
print(df)
