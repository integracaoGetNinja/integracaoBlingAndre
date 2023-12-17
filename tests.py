import xml.etree.ElementTree as ET

# Seu XML
xml_string = """
<retorno>
    <produtos>
        <produto>
            <id>16176791595</id>
            <codigo>793092</codigo>
            <descricao>CAIXA BARRA BANANA</descricao>
            <tipo>P</tipo>
            <situacao>Ativo</situacao>
            <unidade>UNI</unidade>
            <preco>54.0000000000</preco>
            <precocusto>38.0000000000</precocusto>
            <descricaocurta>&lt;p&gt;A barra banana é um alimento rico em diversas vitaminas e minerais. Ela é uma excelente fonte de potássio, um nutriente essencial para o funcionamento adequado do coração, músculos e nervos. Além disso, a barra banana também contém vitamina C, vitamina B6, fibra dietética e ácido fólico.&lt;br /&gt;&lt;br /&gt;Ela pode ser consumida de diversas formas, como por exemplo, em receitas de bolos e tortas, ou simplesmente como um lanche rápido e nutritivo. A barra banana é um alimento versátil e muito beneficioso para a saúde.&lt;/p&gt;</descricaocurta>
            <descricaocomplementar/>
            <datainclusao>2023-12-05</datainclusao>
            <dataalteracao>2023-12-05</dataalteracao>
            <imagethumbnail/>
            <urlvideo/>
            <nomefornecedor>NEBO DISTRIBUIDORA DE ALIMENTOS LTDA</nomefornecedor>
            <codigofabricante/>
            <marca/>
            <class_fiscal>1211.90.90</class_fiscal>
            <cest/>
            <origem>0</origem>
            <idgrupoproduto>0</idgrupoproduto>
            <linkexterno/>
            <observacoes/>
            <grupoproduto/>
            <garantia>0</garantia>
            <descricaofornecedor/>
            <idfabricante>15807426739</idfabricante>
            <categoria>
                <id>5401701</id>
                <descricao>INDUSTRIALIZADOS </descricao>
            </categoria>
            <pesoliq>0.50000</pesoliq>
            <pesobruto>0.50000</pesobruto>
            <estoqueminimo>0.00</estoqueminimo>
            <estoquemaximo>0.00</estoquemaximo>
            <gtin>7898285980659</gtin>
            <gtinembalagem/>
            <larguraproduto>10</larguraproduto>
            <alturaproduto>10</alturaproduto>
            <profundidadeproduto>10</profundidadeproduto>
            <unidademedida>Centímetro</unidademedida>
            <itensporcaixa>0</itensporcaixa>
            <volumes>0</volumes>
            <localizacao/>
            <crossdocking>0</crossdocking>
            <condicao>NÃO ESPECIFICADO</condicao>
            <fretegratis>N</fretegratis>
            <producao>P</producao>
            <datavalidade>2024-01-14</datavalidade>
            <spedtipoitem/>
            <imagem>
                <link>https://33443.cdn.simplo7.net/static/33443/sku/doces.html-barra-cereal-supino-banana-c-choc-light-1660939686760.jpg</link>
                <validade>S/ Validade</validade>
                <tipoarmazenamento>externo</tipoarmazenamento>
            </imagem>
            <estoqueatual>0</estoqueatual>
            <depositos>
                <deposito>
                    <id>14886509737</id>
                    <nome>Geral</nome>
                    <saldo>0</saldo>
                    <desconsiderar>N</desconsiderar>
                    <saldovirtual>0</saldovirtual>
                </deposito>
            </depositos>
        </produto>
    </produtos>
</retorno>
"""

# Parse do XML
root = ET.fromstring(xml_string)

# Altere os valores conforme necessário
root.find(".//preco").text = "666.9000000000"
root.find(".//precocusto").text = "777.0600000000"
root.find(".//estoqueatual").text = "888.978"

# Converta de volta para string
modified_xml = ET.tostring(root, encoding="utf-8").decode("utf-8")

# Imprima o XML modificado
print(modified_xml)
