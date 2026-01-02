# legislacao.py

def get_library():
    """
    SUPER BASE DE DADOS LEGISLATIVA (MASTER MERGE)
    Focada em Ambiente, Agricultura, Clima e Licenciamento.
    """
    return {
        "0. ESTRATÉGIA, CLIMA & BIODIVERSIDADE (Meta-Legislação)": {
            "Lei de Bases do Clima (Lei n.º 98/2021)": {
                "mandato": "Vincula Portugal à neutralidade carbónica em 2050. Cria orçamentos de carbono e obriga a testes de impacto climático na legislação.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/detalhe/lei/98-2021-176905537"
            },
            "Regulamento do Restauro da Natureza (UE) 2024/1991": {
                "mandato": "Meta vinculativa de restaurar 20% das áreas terrestres/marítimas da UE até 2030. Foco crítico em ecossistemas agrícolas e turfeiras.",
                "nivel": "UE",
                "link": "https://eur-lex.europa.eu/eli/reg/2024/1991/oj"
            },
            "PNEC 2030 - Plano Nacional Energia e Clima": {
                "mandato": "Metas nacionais para redução de emissões (55%), renováveis (85% na eletricidade) e eficiência energética para a década 2021-2030.",
                "nivel": "PT",
                "link": "https://apambiente.pt/clima/pnec-2030"
            },
            "Estratégia do Prado ao Prato (Farm to Fork)": {
                "mandato": "Meta UE: Reduzir 50% pesticidas, 20% fertilizantes e atingir 25% de agricultura biológica até 2030.",
                "nivel": "UE",
                "link": "https://food.ec.europa.eu/horizontal-topics/farm-fork-strategy_pt"
            }
        },

        "1. REGIMES TRANSVERSAIS DE LICENCIAMENTO": {
            "RJAIA - Regime Jurídico AIA (DL 151-B/2013 na redação atual)": {
                "mandato": "Obriga à avaliação de impacte ambiental de projetos. Define prazos, tramitação e necessidade de Declaração de Impacte Ambiental (DIA).",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2013-116043164"
            },
            "SIMPLEX AMBIENTAL (DL 11/2023 - Versão Consolidada)": {
                "mandato": "Elimina licenças e atos administrativos desnecessários. Altera regras de AIA e licenciamento hídrico.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/detalhe/decreto-lei/11-2023-207604364"
            },
            "LUA - Licenciamento Único (DL 75/2015 na redação atual)": {
                "mandato": "Cria o Título Único Ambiental (TUA). Agrega todas as licenças ambientais num único ato administrativo.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2015-106567543"
            },
            "REDE NATURA 2000 (DL 140/99 consolidado)": {
                "mandato": "Transpõe Diretivas Aves e Habitats. Protege Zonas Especiais de Conservação e ZPE. Proíbe a deterioração de habitats.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/1999-34460975"
            },
            "RESPONSABILIDADE AMBIENTAL (DL 147/2008)": {
                "mandato": "Princípio do poluidor-pagador. Obriga operadores a constituir garantias financeiras para reparação de danos ambientais.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2008-34484567"
            }
        },

        "2. AGRICULTURA, FLORESTA & SOLOS": {
            "PEPAC Portugal (2023-2027)": {
                "mandato": "Plano Estratégico da PAC. Define Eco-regimes e medidas agroambientais. Estabelece a 'Condicionalidade Reforçada'.",
                "nivel": "PT/UE",
                "link": "https://www.gpp.pt/index.php/pepac/pepac-2023-2027"
            },
            "Regulamento Desflorestação (EUDR) 2023/1115": {
                "mandato": "Proíbe produtos (madeira, soja, bovinos) ligados à desflorestação no mercado da UE. Exige geolocalização das parcelas.",
                "nivel": "UE",
                "link": "https://eur-lex.europa.eu/eli/reg/2023/1115/oj"
            },
            "Lei de Bases da Política Florestal (Lei n.º 33/96)": {
                "mandato": "Define os princípios da gestão florestal sustentável, PROFs e ZIFs.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/detalhe/lei/33-1996-224426"
            },
            "SISTEMA DEFESA FLORESTA (DL 124/2006 atualizado)": {
                "mandato": "Medidas de defesa contra incêndios (DFCI), incluindo faixas de gestão de combustível e limpeza de terrenos.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2006-34493356"
            },
            "NREAP - Pecuária (DL 81/2013 consolidado)": {
                "mandato": "Novo Regime do Exercício da Atividade Pecuária. Licenciamento de explorações e gestão de efluentes.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2013-34766868"
            },
            "ARBORIZAÇÃO (DL 96/2013 RJAAR)": {
                "mandato": "Regime jurídico das ações de arborização. Protege espécies como sobreiro e azinheira.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2013-116043321"
            }
        },

        "3. ÁGUA & SANEAMENTO": {
            "LEI DA ÁGUA (Lei 58/2005 e DL 226-A/2007)": {
                "mandato": "Lei quadro da gestão de recursos hídricos (DQA) e regime de utilização (TURH).",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2005-34563267"
            },
            "Diretiva Nitratos (91/676/CEE)": {
                "mandato": "Proteção das águas contra poluição por nitratos de origem agrícola. Define 'Zonas Vulneráveis' e Códigos de Boas Práticas.",
                "nivel": "UE",
                "link": "https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX:31991L0676"
            },
            "QUALIDADE ÁGUA CONSUMO (DL 306/2007 consolidado)": {
                "mandato": "Regime da qualidade da água para consumo humano. Transpõe Diretiva (UE) 2020/2184.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2007-34512233"
            },
            "SEGURANÇA BARRAGENS (DL 21/2018)": {
                "mandato": "Regulamento de Segurança de Barragens. Normas de projeto, construção e exploração.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2018-114833256"
            }
        },

        "4. ENERGIA & INDÚSTRIA": {
            "SISTEMA ELÉTRICO (DL 15/2022)": {
                "mandato": "Organização do Sistema Elétrico Nacional (SEN). Regula produção, autoconsumo e comunidades de energia.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2022-177343687"
            },
            "GASES RENOVÁVEIS/H2 (DL 62/2020)": {
                "mandato": "Organização do Sistema Nacional de Gás. Hidrogénio Verde e biometano.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2020-141445587"
            },
            "EMISSÕES INDUSTRIAIS (DL 127/2013 - REI)": {
                "mandato": "Regime de Emissões Industriais. Transpõe a Diretiva IED (Prevenção e Controlo Integrados da Poluição).",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2013-34789569"
            },
            "SEVESO III (DL 150/2015)": {
                "mandato": "Prevenção de acidentes graves com substâncias perigosas.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2015-106558967"
            }
        },

        "5. TERRITÓRIO & URBANISMO": {
            "RJUE (DL 555/99 consolidado)": {
                "mandato": "Regime Jurídico da Urbanização e Edificação. Controlo prévio de operações urbanísticas.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/1999-34563452"
            },
            "RAN - Reserva Agrícola (DL 73/2009)": {
                "mandato": "Protege solos de maior aptidão agrícola. Restringe construções não-agrícolas.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/detalhe/decreto-lei/73-2009-540266"
            },
            "REN - Reserva Ecológica (DL 166/2008)": {
                "mandato": "Estrutura biofísica fundamental. Protege dunas, leitos de cheia e arribas.",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2008-34512221"
            },
             "BASES RECURSOS GEOLÓGICOS (Lei 54/2015)": {
                "mandato": "Bases do regime jurídico dos recursos geológicos (Minas e Pedreiras).",
                "nivel": "PT",
                "link": "https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2015-107567789"
            }
        }
    }
