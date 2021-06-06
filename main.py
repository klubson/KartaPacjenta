import fhirpy as fhir
from fhirpy import SyncFHIRClient

HAPI_BASE_URL = "http://hapi.fhir.org/baseR4"

if __name__ == "__main__":

    client = SyncFHIRClient(HAPI_BASE_URL)
    resources = client.resources('Patient')
    resources = resources.limit(10).sort('name')
    patients = resources.fetch()
    #me = patients.pop()
    for me in patients:
        print('Name: ' + me['name'][0]['text'])
        print('Gender: ' + me['gender'])
        print('Date of birth: ' + me['birthDate'])
        print('Identifier: ' + str(me['identifier'][0]['value']))
        print('===================')
    patientIndex = input('Enter for Patient Identifier: ')
    resources2 = client.resources('Observation')
    resources2 = resources2.limit(10)
    observations = resources2.fetch()

