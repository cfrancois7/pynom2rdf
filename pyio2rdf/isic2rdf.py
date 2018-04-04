# python3
"""Transform ISIC classifications into RDF and JSON-LD

Notes:
-----

This package allows to transform ISIC classification (*.txt) into RDF and JSON-LD.
It can transform the ISIC classification into centrally registered identifier
(CRID) and into classes.
The package is compatible with the IEO ontology[1].

[1]: https://github.com/cfrancois7/IEO-ontology

"""

from rdflib import Graph, Literal, Namespace, RDF, RDFS
from pandas import read_csv, DataFrame

ISIC = Namespace('https://unstats.un.org/unsd/cr/registry/')
BFO = OBI = IAO = Namespace('http://purl.obolibrary.org/obo/')
IEO = Namespace('http://www.isterre.fr/ieo/')
IAO.denotes = IAO.IAO_0000219
BFO.has_part = BFO.BFO_0000051
BFO.part_of = BFO.BFO_0000050
# Industrial activity classification (IAC)
IAC_DATABASE = IEO.IEO_0000065
IAC_REGISTRY = IEO.IEO_0000066


def sup_spe_charact(text: str):
    for char in ['\\','`','*',' ','>','#','+','-','.','!','$','\'']:
        if char in text:
            text = text.replace(char, "_")
        elif char in ['{','}','[',']','(',')']:
            text = text.replace(char, "")
    return text


def verify_version() -> int:
    try:
        version_number = int(input('What is the version number of the ISIC Rev classification? :'))
    except:
        print('The version has to be an integer')
        version_number = verify_version()
    return version_number


def isic2crid(data: DataFrame) -> Graph:
    graph = Graph()
    crid_reg = 'ISIC'
    crid_reg_label = 'International Standard Industrial Classification'
    version = str(verify_version())
    graph.add((IAC_REGISTRY, RDFS.label,
               Literal('Industrial activity classification registry', lang='en')))
    graph.add((ISIC[crid_reg], RDF.type, IAC_REGISTRY))
    graph.add((ISIC[crid_reg], RDFS.label, Literal(crid_reg_label)))
    database_id = 'ISIC_Rev'+version
    database_label = 'International Standard Industrial Classification Rev'+version
    graph.add((IAC_DATABASE, RDFS.label,
               Literal('Industrial activity classification version', lang='en')))
    graph.add((ISIC[database_id], RDF.type, IAC_DATABASE))
    graph.add((ISIC[database_id], RDFS.label,
               Literal(database_label)))
    graph.add((ECO[database_id], IAO.denotes, ECO[crid_reg]))
    graph.add((IAO.denotes, RDFS.label,
               Literal('denotes', lang='en')))
    for code in data.index:
        activity_label = data.loc[code][0]
        crid = f'{database_id}_{code}'
        crid_label = f'{database_id}:{code} {activity_label}'
        activity_id = sup_spe_charact(activity_label)
        graph.add((ISIC[activity_id], RDF.type, ISIC.industrial_sector_label))
        graph.add((ISIC[crid], RDF.type, ISIC.classification))
        graph.add((ISIC[crid], RDFS.label, Literal(crid_label, lang='en')))
        graph.add((ISIC[crid], BFO.has_part, ISIC[database_id]))
        graph.add((ISIC[database_id], BFO.part_of, ISIC[crid]))
        graph.add((ISIC[crid], BFO.has_part, ISIC[activity_id]))
        graph.add((ISIC[activity_id], BFO.part_of, ISIC[crid]))
    return graph


def transform_xml(data: DataFrame, path: str):
    graph = isic2crid(data)
    graph.serialize(path, format='xml')


def transform_json(data: DataFrame, path: str):
    graph = isic2crid(data)
    graph.serialize(path, format='json-ld')
