#bin/python3
""" Generate the parent types to link the nomenclature types to the reused
ontologies such as BFO, OBI and IAO.
"""
from rdflib import Graph, Literal, Namespace, RDF, RDFS

# Constant
BFO = OBI = IAO = Namespace('http://purl.obolibrary.org/obo/')
IEO = Namespace('http://www.isterre.fr/ieo/')

def nom_graph() -> Graph:
    """ Create the graph to represent the nomenclature data into the IEO
    ontology.
    """
    graph = Graph()
    # IAO types
    crid_sym = IAO.IAO_0000577
    crid = IAO.IAO_0000578
    crid_reg = IAO.IAO_0000579
    # IAO labels
    crid_label = 'centrally registered identifier'
    crid_reg_label = 'centrally registered identifier registry'
    crid_sym_label = 'centrally registered identifier symbol'
    graph.add((IAO.IAO_0000577, RDFS.label, Literal(crid_sym_label, lang='en')))
    graph.add((IAO.IAO_0000578, RDFS.label, Literal(crid_label, lang='en')))
    graph.add((IAO.IAO_0000579, RDFS.label, Literal(crid_reg_label, lang='en')))
    # IEO types
    reg_version = IEO.IEO_0000043
    lca_reg = IEO.IEO_0000044
    ref_activity = IEO.IEO_0000065
    activity_crid = IEO.IEO_0000066
    activity_reg = IEO.IEO_0000067
    ref_product = IEO.IEO_0000068
    product_crid = IEO.IEO_0000069
    product_reg = IEO.IEO_0000070
    # IEO labels
    reg_ver_label = 'registry version'
    lca_reg_label = 'life cycle database registry'
    ref_activity_label = 'reference activity'
    activity_crid_label = 'reference activity identifier'
    activity_reg_label = 'reference activity registry'
    ref_product_label = 'reference product'
    product_crid_label = 'reference product registry'
    product_reg_label = 'reference product registry'
    graph.add((lca_reg, RDFS.label, Literal(lca_reg_label, lang='en')))
    graph.add((ref_activity, RDFS.label, Literal(ref_activity_label, lang='en')))
    graph.add((activity_crid, RDFS.label, Literal(activity_crid_label, lang='en')))
    graph.add((activity_reg, RDFS.label, Literal(activity_reg_label, lang='en')))
    graph.add((ref_product, RDFS.label, Literal(ref_product_label, lang='en')))
    graph.add((product_crid, RDFS.label, Literal(product_crid_label, lang='en')))
    graph.add((product_reg, RDFS.label, Literal(product_reg_label, lang='en')))
    graph.add((reg_version, RDFS.label, Literal(reg_ver_label, lang='en')))
    # subclass of
    graph.add((ref_activity, RDFS.subClassOf, crid_sym))
    graph.add((ref_product, RDFS.subClassOf, crid_sym))
    graph.add((activity_crid, RDFS.subClassOf, crid))
    graph.add((product_crid, RDFS.subClassOf, crid))
    graph.add((lca_reg, RDFS.subClassOf, crid_reg))
    graph.add((activity_reg, RDFS.subClassOf, crid_reg))
    graph.add((product_reg, RDFS.subClassOf, crid_reg))
    graph.add((reg_version, RDFS.subClassOf, crid_sym))
    return graph
