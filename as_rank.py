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
        as_rank = json_['asn']['rank']
        as_name = json_['asn']['organization']['orgName']
        customer_cone_size = json_['cone']['numberAsns']
        print(json_)
        print(as_rank, as_name, customer_cone_size)
        return dict(as_rank=as_rank, as_name=as_name, customer_cone_size=customer_cone_size)
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
