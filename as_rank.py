import re
import argparse
import sys
import json
import requests

URL = "https://api.asrank.caida.org/v2/graphql"
decoder = json.JSONDecoder()
encoder = json.JSONEncoder()

def query_as_rank(asn):
    query = AsnQuery(asn)
    request = requests.post(URL,json={'query':query})
    if request.status_code == 200:
        json_ = request.json()['data']
        try:
            as_rank = json_['asn']['rank']
        except:
            as_rank = None
        try:
            as_name = json_['asn']['organization']['orgName']
        except:
            as_name = None
        try:
            customer_cone_size = json_['asn']['cone']['numberAsns']
        except:
            customer_cone_size = None
        return (as_rank, as_name, customer_cone_size)
    else:
        print("Query failed to run returned code of %d " % (request.status_code))

def AsnQuery(asn):
    return """{
        asn(asn:"%i") {
            asn
            asnName
            rank
            organization {
                orgId
                orgName
            }
            cliqueMember
            seen
            longitude
            latitude
            cone {
                numberAsns
                numberPrefixes
                numberAddresses
            }
            country {
                iso
                name
            }
            asnDegree {
                provider
                peer
                customer
                total
                transit
                sibling
            }
            announcing {
                numberPrefixes
                numberAddresses
            }
        }
    }""" % (asn)

if __name__ == "__main__":
    print(query_as(3356))
