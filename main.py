import fhirpy as fhir
from fhirpy import SyncFHIRClient

HAPI_BASE_URL = "http://hapi.fhir.org/baseR4"

if __name__ == "__main__":
    client = SyncFHIRClient(HAPI_BASE_URL)
    resources = client.resources('Patient')
    resources = resources.limit(10).sort('name')
    patients = resources.fetch()
    me = patients.pop()
    print(me['name'][0])
