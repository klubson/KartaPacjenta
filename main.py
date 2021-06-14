import fhirpy as fhir
from fhirpy import SyncFHIRClient
from streamlit.components.v1 import html as st_html
import streamlit as st

HAPI_BASE_URL = "http://hapi.fhir.org/baseR4"


def main():
    client = SyncFHIRClient(
        HAPI_BASE_URL
    )
    patients = client.resources('Patient')
    user_input = st.text_input("Name", "")
    if user_input != "":
        patients = patients.search(family__contains=user_input).sort('name')
        results = patients.fetch()
        st.write("Results: " + str(len(results)))
        for patient in results:
            dic = patient.serialize()
            name_s = ""
            for name in dic['name'][0]['given']:
                name_s += name + " "
            st.write(name_s + dic['name'][0]['family'])


if __name__ == "__main__":
    main()
