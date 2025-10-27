import base64

import pandas as pd

#Função para converter a latiude e longitude em formatos validos
def reconstruct_lat(value):
    val_str = str(value)

    # Remove os pontos e troca a virgula por um ponto
    val_str = val_str.replace(".", "").replace(",", ".")

    try:
        num = float(val_str)

        # Divide por dez até chegar no range de latitude/longitude valido
        while abs(num) > 90:
            num /= 10

        return num
    except:
        return None

def PadronizarCupons(dfCupons):
    farmacias = ('Drogasil', 'Drogaria São Paulo', 'Droga Raia')
    clinicasMed = ('Sabin', 'Lavoisier', 'Fleury')
    roupasCal = ('Renner', 'Forever 21', 'Riachuelo')
    restaurantes = ('Ráscal', 'Churrascaria Boi Preto', 'Madero', 'Outback')
    academias = ('Smart Fit', 'Selfit')
    cultural = ('Sesc Carmo', 'Sesc Paulista')
    supermercado = ('Extra', 'Pão de Açúcar', 'Carrefour Express')
    clubes = ('Clube Pinheiros',)
    modaAlt = ('Just Run',)
    cafeterias = ('Octavio Café', 'Café Cultura', 'Starbucks')
    fastfood = ('Açaí no Ponto', "McDonald's", "Habib's", 'Subway', 'Burger King')
    movelDeco = ('Casas Bahia', 'Magazine Luiza', 'Ponto')

    for category, category_name in [
        (farmacias, 'Farmácias e Drogarias'),
        (clinicasMed, 'Clínicas Médicas e Laboratórios'),
        (roupasCal, 'Lojas de Roupas e Calçados'),
        (restaurantes, 'Restaurantes e Gastronomia'),
        (academias, 'Academias e Studios Fitness'),
        (cultural, 'Espaços Culturais e de Experiência Interativa'),
        (supermercado, 'Supermercados e Mercados Express'),
        (clubes, 'Clubes e Centros de Convivência'),
        (modaAlt, 'Lojas de Moda Urbana e Alternativa'),
        (cafeterias, 'Cafeterias e Bistrôs Modernos'),
        (fastfood, 'Lanchonetes e Fast-Food'),
        (movelDeco, 'Lojas de Eletrodomésticos e Utilidades Domésticas')
    ]:
        for estabelecimento in category:
            dfCupons.loc[
                dfCupons['nome_estabelecimento'] == estabelecimento, 'categoria_estabelecimento'] = category_name

    return dfCupons

def PadronizarMassaTeste(dfMassaTeste):
    categories = [
        ('vestuário', 'Havaianas', 'Riachuelo', 'Renner', 'Lojas Americanas'),
        ('outros', 'Livraria Cultura', 'Smart Fit'),
        ('mercado express', 'Pão de Açúcar', 'Extra Mercado'),
        ('farmácia', 'Drogaria São Paulo'),
        ('eletrodoméstico', 'Ponto Frio', 'Kalunga'),
        ('móveis', 'Daiso Japan', 'Fast Shop'),
        ('restaurante', 'Outback', 'Subway')
    ]

    for category_name, *stores in categories:
        for store in stores:
            dfMassaTeste.loc[dfMassaTeste['nome_loja'] == store, 'tipo_loja'] = category_name
    # Utiliza a função acima para realizar a conversão e criar novas colunas
    dfMassaTeste["latitude"] = dfMassaTeste["latitude"].apply(reconstruct_lat)
    dfMassaTeste["longitude"] = dfMassaTeste["longitude"].apply(reconstruct_lat)

    return dfMassaTeste

def PadronizarBasePedestre(dfBasePedestres):
    #Converte as coordenadas
    dfBasePedestres["latitude"] = dfBasePedestres["latitude"].apply(reconstruct_lat)
    dfBasePedestres["longitude"] = dfBasePedestres["longitude"].apply(reconstruct_lat)
    # Padronizando os dados da tabela Base Pedestres com os dados da tabela de base cadastral
    dfBasePedestres.loc[dfBasePedestres['ultimo_tipo_loja'] == 'restaurante', 'ultimo_tipo_loja'] = 'Restaurantes e Gastronomia'
    dfBasePedestres.loc[dfBasePedestres['ultimo_tipo_loja'] == 'mercado express', 'ultimo_tipo_loja'] = 'Supermercados e Mercados Express'
    dfBasePedestres.loc[dfBasePedestres['ultimo_tipo_loja'] == 'farmácia', 'ultimo_tipo_loja'] = 'Farmácias e Drogarias'
    dfBasePedestres.loc[dfBasePedestres['ultimo_tipo_loja'] == 'esportivo', 'ultimo_tipo_loja'] = 'Clubes e Centros de Convivência'
    dfBasePedestres.loc[dfBasePedestres['ultimo_tipo_loja'] == 'móveis', 'ultimo_tipo_loja'] = 'Lojas de Móveis e Decoração'
    dfBasePedestres.loc[dfBasePedestres['ultimo_tipo_loja'] == 'vestuário', 'ultimo_tipo_loja'] = 'Lojas de Roupas e Calçados'
    dfBasePedestres.loc[dfBasePedestres['ultimo_tipo_loja'] == 'eletrodoméstico', 'ultimo_tipo_loja'] = 'Lojas de Eletrodomésticos e Utilidades Domésticas'

    return dfBasePedestres

def PadronizarBaseCadastral(dfBaseCadastral):
    dfBaseCadastral = dfBaseCadastral.drop_duplicates(subset='celular', keep='first')

    return dfBaseCadastral
