from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse

from rdflib.graph import Graph
from rdflib import URIRef, Literal

from semantic_store.rdfstore import rdfstore
from semantic_store.namespaces import NS
from _harvest import harvest_collection, localize_describes


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--purge',
                    dest='purge',
                    help="Purge all triples for this collection and re-harvest."),
        make_option('--url',
                    default=None,
                    dest='url',
                    help="Collection URL (manifest_file or this is required)"),
        make_option('--manifest_file',
                    default=None,
                    dest='manifest_file',
                    help="Collection manifest (this or url is required)"),
        make_option('--uri',
                    default=None,
                    dest='uri',
                    help="Collection URI (required)"),
        make_option('--rep_uri',
                    default=None,
                    dest='rep_uri',
                    help="Repository URI (required)"),
        make_option('--rep_title',
                    default=None,
                    dest='rep_title',
                    help="Repository title (required)"),
        make_option('--store_host',
                    default=None,
                    dest='store_host',
                    help="Store hostname and port (if other than 80) (required)"))


    def handle(self, *args, **options):
        col_url = options['url']
        col_uri = options['uri']
        store_host = options['store_host']
        manifest_file = options['manifest_file']
        rep_uri = options['rep_uri']
        rep_title = options['rep_title']
        if ((not ((col_url or manifest_file) and col_uri)) or 
            (not (store_host and rep_uri and rep_title))):
            print "url or manifest_file and uri arguments are required."
            exit(0)
        rep_uri = URIRef(rep_uri)
        col_uri = URIRef(col_uri)
        rep_g = Graph(store=rdfstore(), identifier=URIRef(rep_uri))
        rep_g.add((rep_uri, NS.rdf['type'], NS.dms['Manifest']))
        rep_g.add((rep_uri, NS.rdf['type'], NS.ore['Aggregation']))
        rep_g.add((rep_uri, NS.dc['title'], Literal(rep_title)))
        local_rel_url = reverse('semantic_store_resources' , 
                                kwargs={'uri': str(rep_uri)})
        local_abs_url = "http://%s%s" % (store_host, local_rel_url)
        rep_g.add((rep_uri, NS.ore['isDescribedBy'], URIRef(local_abs_url)))
        rep_g.add((rep_uri, NS.ore['aggregates'], col_uri))
        rep_g.add((col_uri, NS.ore['isDescribedBy'], URIRef(col_url)))
        localize_describes(store_host, col_uri, col_url, rep_g)
        harvest_collection(col_url, col_uri, store_host, manifest_file)
                
